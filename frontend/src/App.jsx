import { useState } from 'react'
import React from 'react'

function App() {
  const [title, setTitle] = useState('')
  const [theme, setTheme] = useState('')
  const [idea, setIdea] = useState('')
  const [feedback, setFeedback] = useState('')
  const [file, setFile] = useState(null)
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult('')

    const formData = new FormData()
    formData.append('title', title)
    formData.append('theme', theme)
    formData.append('idea', idea)
    formData.append('feedback', feedback)
    if (file) {
      formData.append('feedback_pdf', file)
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/process-feedback/', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResult(data.result)
    } catch (error) {
      console.error('Error:', error)
      setResult('Error processing the feedback.')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-blue-950 flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl font-bold text-white mb-6">
        Agentic AI Feedback & Competitor Analyzer
      </h1>

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-lg bg-white p-6 rounded-lg shadow-md"
      >
        <div className="mb-4">
          <label className="block font-bold mb-1">Project Title</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div className="mb-4">
          <label className="block font-bold mb-1">Project Theme</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            required
          />
        </div>

        <div className="mb-4">
          <label className="block font-bold mb-1">Project Idea</label>
          <textarea
            className="w-full p-2 border rounded"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            required
          ></textarea>
        </div>

        <div className="mb-4">
          <label className="block font-bold mb-1">Feedback (Text)</label>
          <textarea
            className="w-full p-2 border rounded"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          ></textarea>
        </div>

        <div className="mb-4">
          <label className="block font-bold mb-1">Or Upload Feedback PDF</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        <button
          type="submit"
          className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-800"
        >
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {result && (
        <div className="mt-6 w-full max-w-3xl bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">Result:</h2>
          <pre className="whitespace-pre-wrap">{result}</pre>
        </div>
      )}
    </div>
  )
}

export default App
