"use client";
import { useState } from "react";
import Link from "next/link";
import Navbar from "../components/navbar";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Register = () => {
    const [userData, setUserData] = useState({
        username: "",
        email: "",
        full_name: "",
        password: ""
    })
    const registerUser = async () => {
        try {
            const res = await fetch('/register/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            const data = await res.json()
            setUserData({ username: "", email: "", full_name: "", password: "" });
            toast(data.status);
        } catch (err) {
            toast("Internal error, try again.");
        }

    }

    return (
        <div className="h-screen flex">
            <Navbar />
            <main className="p-4 w-full">
                <h2>Register</h2>
                <div className="space-y-2 flex flex-col m-8">
                    <label>Username</label>
                    <input type="text" id="username" placeholder="Enter Username" className="rounded p-2" onChange={(e) => setUserData({ ...userData, username: e.target.value })} />

                    <label>Email</label>
                    <input type="email" id="email" placeholder="Enter Email Address" className="rounded p-2" onChange={(e) => setUserData({ ...userData, email: e.target.value })} />

                    <label>Full Name</label>
                    <input type="text" id="name" placeholder="Enter Full Name" className="rounded p-2" onChange={(e) => setUserData({ ...userData, full_name: e.target.value })} />

                    <label>Password</label>
                    <input type="password" id="password" placeholder="Enter Password" className="rounded p-2" onChange={(e) => setUserData({ ...userData, password: e.target.value })} />

                    <button className="bg-sky-600" onClick={() => registerUser()}>Submit</button>
                </div>
                <p className="text-center">Have an account? <Link href="/login" className="text-sky-600 font-bold hover:underline">Login!</Link></p>
                <ToastContainer />
            </main>
        </div>
    )
}

export default Register;