import React from 'react'
import NavBar from '../components/NavBar.jsx'
import { NavLink } from 'react-router-dom'
import Footer from '../Components/Footer.jsx'

export default function Dashboard() {
  return (
    <div className='bg-green-950 px-20 py-4 text-white '>
      <NavBar/>
      <div className='w-7/12 m-auto py-20 flex flex-col items-center'>
        <h1 className='text-7xl text-center'>Connecting Freelancers with Employers</h1>
        <p className='pt-10 font-thin'>We leverage AI to connect you with your ideal job—no matter where you are.</p>
        <p className='pb-10 font-thin'>Explore over 100,000 opportunities from leading companies to rapidly growing startups.</p>
        <div className='flex justify-between items-center'>
          <NavLink to="/FindJobs" className='px-10 py-4 mx-2 rounded-xl bg-white text-green-950'>Find a Job</NavLink>
          <NavLink to="/UploadJobs" className="border-solid border-white border px-10 py-4 mx-2 rounded-xl">Upload Jobs</NavLink>
        </div>
      </div>
      <div className='grid grid-cols-4  gap-1	'>
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-X05ahxFOrovDPj17QakxksEZXHv6fArgKQ&s" alt="Image" sizes="" srcset="" className='rounded-2xl w-full h-full' />
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQr-69N4-tE96u3WnmP4OtvizoLxglNNPqEzg&s" alt="Image" sizes="" srcset="" className='rounded-2xl w-full h-full'/>
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3NVZyP-N8D8oUe0LTuxOo4PfQRAjn2rknYQ&s" alt="Image" sizes="" srcset="" className='rounded-2xl w-full h-full' />
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTscKF4bRtCncUbANPNl_URAHmZjBtYVyPRbA&s" alt="Image" sizes="" srcset="" className='rounded-2xl w-full h-full row-span-2 '/>
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1-eOrUdswJBcaizOtK3ku1VtEFUjT1xriig&s" alt="Image" sizes="" srcset="" className='rounded-2xl w-full h-full col-span-2 ' />
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-X05ahxFOrovDPj17QakxksEZXHv6fArgKQ&s" alt="Image" sizes="" srcset="" className='rounded-2xl w-full h-full ' />

      </div>
      <Footer/>
    </div>
  )
}
