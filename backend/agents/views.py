import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

serper_tool = SerperDevTool()


def extract_text_from_pdf(pdf_file):
    """Extracts text from uploaded PDF file"""
    text = ""
    pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text


@api_view(['POST'])
@parser_classes([MultiPartParser, JSONParser, FormParser])
def process_feedback(request):
    try:
        # Get data from form-data or JSON
        project_title = request.data.get('title')
        project_theme = request.data.get('theme')
        project_idea = request.data.get('idea')
        feedback_text = request.data.get('feedback') or ""

        # Handle PDF if uploaded
        pdf_file = request.FILES.get('feedback_pdf')
        pdf_text = ""

        if pdf_file:
            pdf_text = extract_text_from_pdf(pdf_file)

        # Combine both text feedback and PDF extracted text
        combined_feedback = f"{feedback_text}\n{pdf_text}".strip()

        if not combined_feedback:
            return JsonResponse({'error': 'No feedback provided via text or PDF.'}, status=400)

        ####### CrewAI Setup (same as before) #######
        feedback_collector = Agent(
            role="Feedback Collection Specialist",
            goal="Aggregate peer feedback from PDFs, sheets, text, emoji, screenshots into structured data.",
            backstory="Expert at transforming unstructured feedback into clean datasets.",
            llm="gemini-2.0-flash",
            verbose=True
        )

        feedback_task = Task(
            description=f"""
            Process the following peer feedback:

            {combined_feedback}

            Convert this into a JSON format with clear individual feedback entries.
            Handle emojis, images, messy text — structure it with fields like: feedback_id, content.
            """,
            agent=feedback_collector
        )

        feedback_summarizer = Agent(
            role="Feedback Summarizer",
            goal="Categorize feedback into Positive, Negative, and Suggestions with recurring themes.",
            backstory="A skilled analyst who summarizes peer feedback for improvements.",
            llm="gemini-2.0-flash",
            verbose=True
        )

        summarizer_task = Task(
            description="""
            Summarize the structured feedback into:
            - Positive points
            - Negative points
            - Suggestions for improvements
            Also highlight any recurring patterns.
            """,
            agent=feedback_summarizer
        )

        competitor_agent = Agent(
            role="Competitor Research Specialist",
            goal="Find top 2-3 relevant competitor products based on the project details.",
            backstory="A market researcher skilled at finding competitors using the web.",
            llm="gemini-2.0-flash",
            tools=[serper_tool],
            verbose=True
        )

        competitor_task = Task(
            description=f"""
            Given the project idea "{project_idea}", title "{project_title}", and theme "{project_theme}",
            use web search to find top 2-3 competitor apps/products.
            Provide their names, descriptions, and reference links.
            """,
            agent=competitor_agent
        )

        review_analysis_agent = Agent(
            role="Review Analysis Specialist",
            goal="Extract UX gaps, feature requests, and pain points from competitor reviews.",
            backstory="Expert in extracting key insights from user reviews.",
            llm="gemini-2.0-flash",
            verbose=True
        )

        review_task = Task(
            description="""
            Analyze reviews of the competitors discovered.
            Extract insights categorized as:
            - Design
            - Function
            - Experience
            Separate into Positive and Negative observations.
            """,
            agent=review_analysis_agent
        )

        refinement_agent = Agent(
            role="Refinement Strategist",
            goal="Synthesize feedback and competitor analysis to generate strategic improvements.",
            backstory="Product strategist providing actionable improvement plans for project success.",
            llm="gemini-2.0-flash",
            verbose=True
        )

        refinement_task = Task(
            description="""
            Combine peer feedback summaries and competitor insights to suggest improvements for the project.
            Provide recommendations for:
            - Scope changes
            - UX improvements
            - New features
            - Suggestions for further development
            Return this as a well-structured report.
            """,
            agent=refinement_agent
        )

        crew = Crew(
            agents=[
                feedback_collector,
                feedback_summarizer,
                competitor_agent,
                review_analysis_agent,
                refinement_agent
            ],
            tasks=[
                feedback_task,
                summarizer_task,
                competitor_task,
                review_task,
                refinement_task
            ],
            process=Process.sequential,
            verbose=True
        )

        result = crew.run()

        return JsonResponse({'result': result}, status=200)

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return JsonResponse({
            'error': str(e),
            'traceback': traceback_str
        }, status=500)


def welcome(request):
    return JsonResponse({'message': 'Welcome to the Agentic AI Backend!'})
