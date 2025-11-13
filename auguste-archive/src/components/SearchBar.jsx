function SearchBar({ searchQuery, setSearchQuery, selectedTags, toggleTag, allTags }) {
  return (
    <div className="mb-8 bg-white rounded-xl shadow-lg p-6">
      <div className="mb-4">
        <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
          Search Content
        </label>
        <input
          id="search"
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by title, topic, or keyword..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filter by Tags
        </label>
        <div className="flex flex-wrap gap-2">
          {allTags.map(tag => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition ${
                selectedTags.includes(tag)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
        {selectedTags.length > 0 && (
          <button
            onClick={() => toggleTag(selectedTags[0])}
            className="mt-2 text-sm text-blue-600 hover:text-blue-800"
          >
            Clear filters
          </button>
        )}
      </div>
    </div>
  )
}

export default SearchBar
