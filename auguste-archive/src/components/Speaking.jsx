function Speaking({ events, searchQuery }) {
  const filteredEvents = events.filter(event => {
    if (!searchQuery) return true
    return (
      event.event.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.organization.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (event.topic && event.topic.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (event.topics && event.topics.some(t => t.toLowerCase().includes(searchQuery.toLowerCase())))
    )
  })

  if (filteredEvents.length === 0 && searchQuery) return null

  return (
    <section className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="mr-3">🎤</span>
        Speaking Engagements
      </h2>

      <div className="grid md:grid-cols-2 gap-6">
        {filteredEvents.map((event, idx) => (
          <div
            key={idx}
            className="border-2 border-gray-200 rounded-lg p-6 hover:border-blue-400 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {event.event}
            </h3>
            <p className="text-gray-600 mb-2">{event.organization}</p>
            <p className="text-sm text-gray-500 mb-3">
              {event.year || event.period} • {event.role}
            </p>

            {event.topic && (
              <p className="text-sm text-gray-700 mb-2">
                <span className="font-medium">Topic:</span> {event.topic}
              </p>
            )}

            {event.format && (
              <p className="text-sm text-gray-700 mb-2">
                <span className="font-medium">Format:</span> {event.format}
              </p>
            )}

            {event.topics && (
              <div className="mb-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Topics:</p>
                <div className="flex flex-wrap gap-2">
                  {event.topics.map((topic, tidx) => (
                    <span
                      key={tidx}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {event.description && (
              <p className="text-sm text-gray-700 mb-3">{event.description}</p>
            )}

            {event.url && (
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center"
              >
                Learn More →
              </a>
            )}
          </div>
        ))}
      </div>

      {filteredEvents.length === 0 && searchQuery && (
        <p className="text-gray-500 text-center py-8">
          No speaking engagements match your search criteria.
        </p>
      )}
    </section>
  )
}

export default Speaking
