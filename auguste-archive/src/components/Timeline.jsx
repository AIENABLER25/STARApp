function Timeline({ timeline, searchQuery }) {
  const filteredTimeline = timeline.filter(item => {
    if (!searchQuery) return true
    return (
      item.event.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.details.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.year.toString().includes(searchQuery)
    )
  })

  if (filteredTimeline.length === 0 && searchQuery) return null

  const getCategoryColor = (category) => {
    const colors = {
      'Education': 'bg-blue-100 text-blue-800 border-blue-300',
      'Career': 'bg-green-100 text-green-800 border-green-300',
      'Publication': 'bg-purple-100 text-purple-800 border-purple-300',
      'Initiative': 'bg-orange-100 text-orange-800 border-orange-300',
      'Research': 'bg-indigo-100 text-indigo-800 border-indigo-300',
      'Recognition': 'bg-yellow-100 text-yellow-800 border-yellow-300'
    }
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  return (
    <section className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="mr-3">⏳</span>
        Timeline
      </h2>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 to-indigo-500" />

        <div className="space-y-8">
          {filteredTimeline.map((item, idx) => (
            <div key={idx} className="relative pl-20">
              {/* Timeline dot */}
              <div className="absolute left-6 top-2 w-5 h-5 rounded-full bg-blue-600 border-4 border-white shadow" />

              {/* Content */}
              <div className={`border-2 rounded-lg p-4 ${getCategoryColor(item.category)}`}>
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-bold text-lg">{item.year}</span>
                  <span className="text-xs font-semibold px-2 py-1 bg-white rounded">
                    {item.category}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{item.event}</h3>
                <p className="text-sm text-gray-700">{item.details}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {filteredTimeline.length === 0 && searchQuery && (
        <p className="text-gray-500 text-center py-8">
          No timeline events match your search criteria.
        </p>
      )}
    </section>
  )
}

export default Timeline
