import React from "react";
import { useState } from "react";
import { PlusCircle, Dot } from "lucide-react";
import CustomInput from "../Components/CustomInput";
import NavBar from "../Components/NavBar";

function UploadJobsPage() {
  const [activeDescription, setActiveDescription] = useState();
  const [activeBudget, setActiveBudget] = useState();
  const [activeAIPowered, setActiveAIPowered] = useState();
  const [activeCompeleted, setActiveCompeleted] = useState();
  return (
    <div>
      <NavBar />
      {/* <h1 className='text-3xl font-medium text-center text-green-950 pt-2'>Our decentralized job marketplace, powered by AI recommendations and blockchain security, ensures a seamless hiring experience.</h1> */}
      <div className="pt-10">
        <h2 className="text-center text-3xl font-bold text-green-950">
          Job posting guide
        </h2>
        <div className=" p-6 rounded-xl border-4 border-gray-300 w-9/12 m-auto text-gray-500 mt-5">
          <div className="flex justify-between">
            <h3 className="font-semibold text-xl text-green-950">
              Job Title & Description
            </h3>
            <div
              className="cursor-pointer"
              onClick={() => setActiveDescription(!activeDescription)}
            >
              <PlusCircle />
            </div>
          </div>
          {activeDescription && (
            <div className="px-1 font-medium text-lg pt-2 ">
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Use a clear & specific title (e.g., "React Developer for Web3
                App")
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Provide detailed requirements, skills needed & expected
                deliverables
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Specify project type (one-time, ongoing, or contract-based)
              </div>
            </div>
          )}
        </div>
        <div className=" p-6 rounded-xl border-4 border-gray-300 w-9/12 m-auto text-gray-500 mt-5">
          <div className="flex justify-between">
            <h3 className="font-semibold text-xl text-green-950">
              Budget & Payment
            </h3>
            <div
              className="cursor-pointer"
              onClick={() => setActiveBudget(!activeBudget)}
            >
              <PlusCircle />
            </div>
          </div>
          {activeBudget && (
            <div className="px-1 font-medium text-lg pt-2">
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" /> Set a realistic budget in USDT
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Funds are held in escrow & released upon job completion
              </div>
            </div>
          )}
        </div>
        <div className=" p-6 rounded-xl border-4 border-gray-300 w-9/12 m-auto text-gray-500 mt-5">
          <div className="flex justify-between">
            <h3 className="font-semibold text-xl text-green-950">
              AI-Powered Freelancer Matching
            </h3>
            <div
              className="cursor-pointer"
              onClick={() => setActiveAIPowered(!activeAIPowered)}
            >
              <PlusCircle />
            </div>
          </div>
          {activeAIPowered && (
            <div className="px-1 font-medium text-lg pt-2">
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" /> AI recommends top freelancers
                based on skills & experience
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                You can auto-assign a job
              </div>
            </div>
          )}
        </div>
        <div className=" p-6 rounded-xl border-4 border-gray-300 w-9/12 m-auto text-gray-500 mt-5">
          <div className="flex justify-between">
            <h3 className="font-semibold text-xl text-green-950">
              {" "}
              Completing & Closing a Job
            </h3>
            <div
              className="cursor-pointer"
              onClick={() => setActiveCompeleted(!activeCompeleted)}
            >
              <PlusCircle />
            </div>
          </div>
          {activeCompeleted && (
            <div className="px-1 font-medium text-lg pt-2">
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Mark job as complete after review
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Release payment securely via escrow
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" /> Cancel job (if no freelancer is
                assigned) for a refund
              </div>
              <div className="flex items-center">
                {" "}
                <Dot size={40} color="black" />
                Post your job now & let AI find the best talent for you!
              </div>
            </div>
          )}
        </div>
      </div>
      <form className="w-4/12 m-auto bg-gray-100 my-10 grid p-6">
        <h1 className="text-3xl font-semibold text-center">Upload Job</h1>
        <CustomInput placeholder="Enter title" label="Title" type="text" />
        <CustomInput
          placeholder="description"
          label="Description"
          type="text"
        />
        <CustomInput placeholder="budget" label="budget" type="text" />
        <button className="bg-green-950 rounded-xl px-6 py-3 text-white w-4/12 text-lg mt-10 justify-self-end">
          Upload job
        </button>
      </form>
    </div>
  );
}

export default UploadJobsPage;
