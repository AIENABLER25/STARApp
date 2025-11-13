function Biography({ data, searchQuery }) {
  const filterBySearch = (text) => {
    if (!searchQuery) return true
    return text.toLowerCase().includes(searchQuery.toLowerCase())
  }

  const matchesSearch =
    filterBySearch(data.name) ||
    filterBySearch(data.title) ||
    data.careerHighlights.some(h => filterBySearch(h.role) || filterBySearch(h.organization))

  if (searchQuery && !matchesSearch) return null

  return (
    <section className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="mr-3">👤</span>
        Biography
      </h2>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Education */}
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Education</h3>
          <div className="space-y-4">
            {data.education.map((edu, idx) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-4">
                <p className="font-semibold text-gray-900">{edu.degree}</p>
                <p className="text-gray-600">{edu.institution}</p>
                <p className="text-sm text-blue-600">{edu.honor}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Career Highlights */}
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Career Highlights</h3>
          <div className="space-y-4">
            {data.careerHighlights.map((career, idx) => (
              <div key={idx} className="border-l-4 border-indigo-500 pl-4">
                <p className="font-semibold text-gray-900">{career.role}</p>
                <p className="text-gray-600">{career.organization}</p>
                <p className="text-sm text-gray-500">{career.period}</p>
                <p className="text-sm text-gray-700 mt-1">{career.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recognition */}
      <div className="mt-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Recognition & Awards</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {data.recognition.map((award, idx) => (
            <div key={idx} className="bg-gradient-to-r from-yellow-50 to-amber-50 rounded-lg p-4">
              <p className="font-semibold text-gray-900">{award.award}</p>
              <p className="text-sm text-gray-600">{award.year || award.period}</p>
              {award.description && (
                <p className="text-sm text-gray-700 mt-1">{award.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Biography
