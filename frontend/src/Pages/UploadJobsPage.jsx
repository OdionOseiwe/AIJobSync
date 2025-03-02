import React from 'react'
import NavBar from '../components/NavBar'
import { useState } from 'react'

function UploadJobsPage() {
    const [activeDescription, setActiveDescription] = useState();
    const [activeBudget, setActiveBudget] = useState()
  return (
    <div>
      <NavBar/>
      {/* <h1 className='text-3xl font-medium text-center text-green-950 pt-2'>Our decentralized job marketplace, powered by AI recommendations and blockchain security, ensures a seamless hiring experience.</h1> */}
        <div className='pt-10'>
            <h2 className='text-center text-3xl font-bold text-green-950'>Job posting guide</h2>
            <div className=' p-6 rounded-xl border-4 border-gray-300 w-9/12 m-auto text-gray-500 mt-5'>
                <div className='flex justify-between'>
                    <h3 className='font-semibold text-xl text-green-950'>Job Title & Description</h3>
                    <div className='cursor-pointer' onClick={()=> setActiveDescription(!activeDescription)}>dropdown</div>
                </div>
                {activeDescription && 
                        <ul className='px-1 font-medium text-lg pt-4'>
                            <li>Use a clear & specific title (e.g., "React Developer for Web3 App")</li>
                            <li>Provide detailed requirements, skills needed & expected deliverables
                            </li>
                            <li>Specify project type (one-time, ongoing, or contract-based)
                            </li>
                        </ul>  
                        
                }
            </div>
            <div className=' p-6 rounded-xl border-4 border-gray-300 w-9/12 m-auto text-gray-500 mt-5'>
                <div className='flex justify-between'>
                    <h3 className='font-semibold text-xl text-green-950'>Budget & Payment</h3>
                    <div className='cursor-pointer' onClick={()=> setActiveBudget(!activeBudget)}>dropdown</div>
                </div>
                {activeBudget && 
                        <ul className='px-1 font-medium text-lg pt-4'>
                            <li> Set a realistic budget in USDT</li>
                            <li>Funds are held in escrow & released upon job completion</li>
                        </ul>  
                        
                }
            </div>
        </div>
      <p>

      </p>
    </div>
  )
}

export default UploadJobsPage
