import React from "react";
import CustomInput from "../Components/CustomInput";
import NavBar from "../Components/NavBar";
function RegisterPage() {
  return (
    <div>
      <NavBar />
      <h1 className="text-3xl font-semibold text-center text-green-950 pt-10">
        Welcome to AIJobSync – AI-Powered Job Matching!
      </h1>
      <p className="text-neutral-600 font-thin text-center">
        Register as a freelancer or employer and let AI connect you with the
        right opportunities. Secure, decentralized, and efficient!
      </p>
      <p className="text-neutral-600 font-thin text-center">
        Create a profile with your skills stored securely via IPFS.Get
        AI-powered job recommendations.Earn in crypto with secure payments
      </p>
      <form className=" w-4/12 m-auto bg-gray-100 my-10 grid p-6">
        <h1 className="text-3xl font-semibold text-center text-green-950 ">
          Register as Freelancer
        </h1>
        <CustomInput placeholder="Enter your name" label="Name" type="text" />
        <CustomInput placeholder="Ipfs hash" label="IPFS hash" type="text" />
        <button className="bg-green-950 rounded-xl px-6 py-3 text-white inline w-28 text-lg mt-10 justify-self-end">
          register
        </button>
      </form>
    </div>
  );
}

export default RegisterPage;
