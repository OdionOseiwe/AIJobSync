import React from 'react'
import NavBar from '../Components/NavBar';

function FindJobs() {
  return (
    <div>
      <NavBar/>
      <div className='px-10 py-5'>
        <div>
          <h1 className='text-3xl font-semibold'>Find your dream job</h1>
          <p className='text-neutral-600 font-thin'>Looking for jobs? Browse our lastest job openings to view and apply to the best job today!</p>
        </div>
        <div></div>
      </div>
    </div>
  )
}

export default FindJobs
