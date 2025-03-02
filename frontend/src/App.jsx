import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Pages/LandingPage'
import FindJobs from './Pages/FindJobsPage';
import RegisterPage from './Pages/RegisterPage';
import UploadJobsPage from './Pages/UploadJobsPage';


function App() {
  const [count, setCount] = useState(0)

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/FindJobs" element={<FindJobs />} />
        <Route path="/Register" element={<RegisterPage />} />
        <Route path="/UploadJobs" element={<UploadJobsPage />} />
      </Routes>
    </Router>
  )
}

export default App
