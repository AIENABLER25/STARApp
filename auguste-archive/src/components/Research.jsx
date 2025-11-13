function Research({ publications, searchQuery, selectedTags }) {
  const filteredPublications = publications.filter(pub => {
    const matchesSearch = !searchQuery ||
      pub.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pub.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pub.organization.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesTags = selectedTags.length === 0 ||
      (pub.tags && selectedTags.some(tag => pub.tags.includes(tag)))

    return matchesSearch && matchesTags
  })

  if (filteredPublications.length === 0 && searchQuery) return null

  return (
    <section className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="mr-3">📊</span>
        Research & Publications
      </h2>

      <div className="space-y-6">
        {filteredPublications.map((pub) => (
          <div
            key={pub.id}
            className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {pub.title}
                </h3>
                <div className="flex items-center gap-3 text-sm text-gray-600 mb-2">
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                    {pub.type}
                  </span>
                  <span>{pub.year}</span>
                  <span>•</span>
                  <span>{pub.organization || pub.publisher}</span>
                </div>
              </div>
            </div>

            <p className="text-gray-700 mb-3">{pub.description}</p>

            {pub.keyFindings && (
              <div className="mb-3">
                <p className="font-medium text-gray-800 mb-2">Key Findings:</p>
                <ul className="list-disc list-inside space-y-1">
                  {pub.keyFindings.map((finding, idx) => (
                    <li key={idx} className="text-sm text-gray-700">
                      {finding}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {pub.tags && (
              <div className="flex flex-wrap gap-2 mb-3">
                {pub.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {pub.url && (
              <a
                href={pub.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center"
              >
                View Publication →
              </a>
            )}
          </div>
        ))}
      </div>

      {filteredPublications.length === 0 && (
        <p className="text-gray-500 text-center py-8">
          No publications match your search criteria.
        </p>
      )}
    </section>
  )
}

export default Research
