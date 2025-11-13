function Initiatives({ initiatives, searchQuery, selectedTags }) {
  const filteredInitiatives = initiatives.filter(initiative => {
    const matchesSearch = !searchQuery ||
      initiative.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      initiative.description.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesSearch
  })

  if (filteredInitiatives.length === 0 && searchQuery) return null

  return (
    <section className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="mr-3">🚀</span>
        Key Initiatives
      </h2>

      <div className="space-y-8">
        {filteredInitiatives.map((initiative, idx) => (
          <div
            key={idx}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {initiative.name}
                </h3>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <span className="bg-blue-600 text-white px-3 py-1 rounded-full">
                    Launched {initiative.launched}
                  </span>
                  <span>{initiative.organization}</span>
                </div>
              </div>
            </div>

            <p className="text-gray-700 mb-4">{initiative.description}</p>

            <div className="bg-white rounded-lg p-4 mb-4">
              <p className="font-semibold text-gray-900 mb-2">Impact:</p>
              <p className="text-gray-700">{initiative.impact}</p>
            </div>

            {initiative.keyComponents && (
              <div className="mb-4">
                <p className="font-semibold text-gray-900 mb-2">Key Components:</p>
                <ul className="list-disc list-inside space-y-1">
                  {initiative.keyComponents.map((component, cidx) => (
                    <li key={cidx} className="text-gray-700">
                      {component}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {initiative.mediaChannels && (
              <div className="mb-4">
                <p className="font-semibold text-gray-900 mb-2">Media Channels:</p>
                <div className="flex flex-wrap gap-2">
                  {initiative.mediaChannels.map((channel, cidx) => (
                    <span
                      key={cidx}
                      className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm"
                    >
                      {channel}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {initiative.methodology && (
              <div className="mb-4">
                <p className="font-semibold text-gray-900 mb-2">Methodology:</p>
                <p className="text-gray-700">{initiative.methodology}</p>
              </div>
            )}

            {initiative.goal && (
              <div className="bg-yellow-50 rounded-lg p-4 mb-4 border border-yellow-200">
                <p className="font-semibold text-gray-900 mb-1">Goal:</p>
                <p className="text-gray-700">{initiative.goal}</p>
              </div>
            )}

            {initiative.url && (
              <a
                href={initiative.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
              >
                Learn More →
              </a>
            )}
          </div>
        ))}
      </div>

      {filteredInitiatives.length === 0 && searchQuery && (
        <p className="text-gray-500 text-center py-8">
          No initiatives match your search criteria.
        </p>
      )}
    </section>
  )
}

export default Initiatives
