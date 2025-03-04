import React from 'react'
import AILogo from "../assets/AILogo.png"
import { NavLink } from 'react-router-dom'

function Footer() {
  return (
    <div className='pt-20 pb-10'>
        <div className="flex items-center"> <img src={AILogo} alt="Logo" className='w-14 h-12' /> <p className='text-3xl font-semibold'>Ijobsync</p></div>
        <div className='flex pt-6 text-lg font-light'>
            <NavLink to="/FindJobs" className={`pr-4`}> Find Jobs</NavLink>
            <NavLink to="/UploadJobs " className={`pl-6`}> Upload Jobs</NavLink>
        </div>
        <hr className='mt-6'/>
        <div className='text-lg font-light mt-4'> &copy;AIJobSync. All rights reserved</div>
    </div>
  )
}

export default Footer
