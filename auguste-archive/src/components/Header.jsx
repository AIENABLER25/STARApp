function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Auguste Archive</h1>
            <p className="text-blue-100 text-sm">
              Centralizing 20+ Years of Impact
            </p>
          </div>
          <div className="flex gap-4">
            <a
              href="https://opportunityatwork.org"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition"
            >
              Visit Opportunity@Work
            </a>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
