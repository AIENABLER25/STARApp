function Media({ mediaData, searchQuery }) {
  const filterMedia = (items) => {
    if (!searchQuery) return items
    return items.filter(item =>
      item.outlet?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.topic?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.program?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }

  const filteredTV = filterMedia(mediaData.television)
  const filteredPrint = filterMedia(mediaData.print)
  const filteredRadio = filterMedia(mediaData.radio)
  const filteredPodcasts = filterMedia(mediaData.podcasts)

  const hasResults = filteredTV.length > 0 || filteredPrint.length > 0 ||
    filteredRadio.length > 0 || filteredPodcasts.length > 0

  if (searchQuery && !hasResults) return null

  return (
    <section className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="mr-3">📺</span>
        Media Appearances
      </h2>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Television */}
        {filteredTV.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📺</span>
              Television
            </h3>
            <div className="space-y-3">
              {filteredTV.map((item, idx) => (
                <div key={idx} className="bg-blue-50 rounded-lg p-4">
                  <p className="font-semibold text-gray-900">{item.outlet}</p>
                  <p className="text-sm text-gray-700">{item.topic}</p>
                  <p className="text-xs text-gray-500 mt-1">{item.type} • {item.year}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Print */}
        {filteredPrint.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📰</span>
              Print Media
            </h3>
            <div className="space-y-3">
              {filteredPrint.map((item, idx) => (
                <div key={idx} className="bg-indigo-50 rounded-lg p-4">
                  <p className="font-semibold text-gray-900">{item.outlet}</p>
                  <p className="text-sm text-gray-700">{item.topic}</p>
                  <p className="text-xs text-gray-500 mt-1">{item.type} • {item.year}</p>
                  {item.note && (
                    <p className="text-xs text-blue-600 mt-1">{item.note}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Radio */}
        {filteredRadio.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📻</span>
              Radio
            </h3>
            <div className="space-y-3">
              {filteredRadio.map((item, idx) => (
                <div key={idx} className="bg-purple-50 rounded-lg p-4">
                  <p className="font-semibold text-gray-900">{item.outlet}</p>
                  {item.program && (
                    <p className="text-sm text-gray-600">{item.program}</p>
                  )}
                  <p className="text-sm text-gray-700">{item.topic}</p>
                  <p className="text-xs text-gray-500 mt-1">{item.type} • {item.year}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Podcasts */}
        {filteredPodcasts.length > 0 && (
          <div className="md:col-span-2">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🎙️</span>
              Podcasts
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {filteredPodcasts.map((item, idx) => (
                <div key={idx} className="bg-green-50 rounded-lg p-4">
                  <p className="font-semibold text-gray-900">{item.name}</p>
                  {item.episode && (
                    <p className="text-sm text-gray-700 mb-1">
                      {Array.isArray(item.episodes) ? item.episodes.join(', ') : item.episode}
                    </p>
                  )}
                  {item.host && (
                    <p className="text-sm text-gray-600">Host: {item.host}</p>
                  )}
                  <p className="text-sm text-gray-700 mt-2">{item.description}</p>
                  {item.topics && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {item.topics.map((topic, tidx) => (
                        <span
                          key={tidx}
                          className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block"
                    >
                      Listen →
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {!hasResults && searchQuery && (
        <p className="text-gray-500 text-center py-8">
          No media appearances match your search criteria.
        </p>
      )}
    </section>
  )
}

export default Media
