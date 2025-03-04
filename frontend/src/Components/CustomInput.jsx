import React from 'react'

function CustomInput({placeholder,label,type,value,onChange}) {
  return (
    <div className='flex flex-col pt-6'>
      <label className='font-semibold'>{label}</label>
      <input   placeholder={placeholder} type={type} value={value} onChange={onChange}  className=' border-gray-300 outline-none w-full h-10 border-2 rounded-lg p-2 focus:border-gray-600 text-gray-600'/>
    </div>
  )
}

export default CustomInput
