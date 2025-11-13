import { useState, useMemo } from 'react'
import { augusteData, contentCategories, allTags } from './data/augusteContent'
import Header from './components/Header'
import Biography from './components/Biography'
import Research from './components/Research'
import Media from './components/Media'
import Speaking from './components/Speaking'
import Initiatives from './components/Initiatives'
import Timeline from './components/Timeline'
import SearchBar from './components/SearchBar'

function App() {
  const [activeCategory, setActiveCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTags, setSelectedTags] = useState([])

  const toggleTag = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Dr. Byron Auguste
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            CEO & Co-founder, Opportunity@Work
          </p>
          <p className="text-lg text-gray-500 max-w-3xl mx-auto">
            20+ years of research, media, and advocacy transforming workforce development
            and economic opportunity in America
          </p>
        </div>

        {/* Search and Filter */}
        <SearchBar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          selectedTags={selectedTags}
          toggleTag={toggleTag}
          allTags={allTags}
        />

        {/* Category Navigation */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3 justify-center">
            {contentCategories.map(category => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`px-6 py-3 rounded-lg font-medium transition-all ${
                  activeCategory === category.id
                    ? 'bg-blue-600 text-white shadow-lg scale-105'
                    : 'bg-white text-gray-700 hover:bg-blue-50 shadow'
                }`}
              >
                <span className="mr-2">{category.icon}</span>
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Content Sections */}
        <div className="space-y-12">
          {(activeCategory === 'all' || activeCategory === 'biography') && (
            <Biography data={augusteData.biography} searchQuery={searchQuery} />
          )}

          {(activeCategory === 'all' || activeCategory === 'research') && (
            <Research
              publications={augusteData.researchPublications}
              searchQuery={searchQuery}
              selectedTags={selectedTags}
            />
          )}

          {(activeCategory === 'all' || activeCategory === 'media') && (
            <Media
              mediaData={augusteData.mediaAppearances}
              searchQuery={searchQuery}
            />
          )}

          {(activeCategory === 'all' || activeCategory === 'speaking') && (
            <Speaking
              events={augusteData.speakingEngagements}
              searchQuery={searchQuery}
            />
          )}

          {(activeCategory === 'all' || activeCategory === 'initiatives') && (
            <Initiatives
              initiatives={augusteData.keyInitiatives}
              searchQuery={searchQuery}
              selectedTags={selectedTags}
            />
          )}

          {(activeCategory === 'all' || activeCategory === 'biography') && (
            <Timeline
              timeline={augusteData.timeline}
              searchQuery={searchQuery}
            />
          )}
        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-gray-200 text-center text-gray-500">
          <p className="mb-2">
            This archive centralizes Dr. Byron Auguste's contributions to workforce development,
            economic policy, and social mobility.
          </p>
          <p className="text-sm">
            For more information, visit{' '}
            <a
              href="https://opportunityatwork.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800"
            >
              Opportunity@Work
            </a>
          </p>
          <p className="text-xs mt-4">
            Last updated: November 2024
          </p>
        </footer>
      </main>
    </div>
  )
}

export default App
