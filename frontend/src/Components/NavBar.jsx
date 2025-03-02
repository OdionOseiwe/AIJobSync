import React from 'react'
import { NavLink } from 'react-router-dom';
import AILogo from "../assets/AILogo.png"

function NavBar() {
  return (
    <div className='flex justify-between text-lg font-thin  bg-green-950 items-center text-white px-20 py-4'>
      <div className=""> <img src={AILogo} alt="Logo" className='w-20 h-14' /> <p>AIjobsync</p></div>
      <nav>
        <NavLink to="/" className={({isActive})=> `p-3 ${isActive ? 'border-b-2': ''}`}>Home</NavLink>
        <NavLink to="/FindJobs" className={({isActive})=> `p-3 ${isActive ? 'border-b-2': ''}`}> Find Jobs</NavLink>
        <NavLink to="/UploadJobs" className={({isActive})=> `p-3 ${isActive ? 'border-b-2': ''}`}> Upload Jobs</NavLink>
        <NavLink to="/About Us" className={({isActive})=> `p-3 ${isActive ? 'border-b-2': ''}`}> About us</NavLink>
      </nav>
      <div className='flex justify-between items-center'>
          <NavLink to="/FindJobs" className='px-6 py-3 mx-2 rounded-xl bg-white text-green-950'>Connect Wallet</NavLink>
          <NavLink to="/Register" className="border-solid border-white border px-6 py-3 mx-2 rounded-xl">Register</NavLink>
        </div>
    </div>
  )
}

export default NavBar
