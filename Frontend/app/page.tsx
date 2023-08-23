'use client';
import { useEffect, useState } from "react";
import Navbar from './components/navbar'
import { useDropzone } from 'react-dropzone';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Link from "next/link";
import ReactLoading from 'react-loading';

export default function Home() {
    const { acceptedFiles, getRootProps, getInputProps } = useDropzone();
    const [loggedIn, setLoggedIn] = useState(false);
    const [loading, setLoading] = useState(false);
    const [translated, setTranslated] = useState(false);
    useEffect(() => {
        fetch("/api")
        .then(res => res.json())
        .then(data => setLoggedIn(data.loggedIn))
    }, [])
    const files = acceptedFiles.map(file => (
        <li key={file.path}>{file.path}</li>
    ));
    const submitFiles = async () => {
        if (!loggedIn) {
            toast("Please log in");
            return;
        }
        if (acceptedFiles[0] === undefined) {
            toast("Empty file");
            return;
        }
        if (acceptedFiles[0].size/1024/1024 > 50) {
            toast("File must be less than 50MB");
            return;
        }
        try {
            setLoading(true);
            const formData = new FormData();
            formData.append("file", acceptedFiles[0]);
            fetch("/api", {
                method: 'POST',
                body: formData
            })
                .then(res => res.json())
                .then(data => { toast(data.status); setLoading(false); setTranslated(true) });
        } catch (err) { toast("Internal error, try again"); setLoading(false); }
    }
    return (
        <div className="h-screen flex">
            <Navbar />
            <main className="p-4 w-full">
                {loggedIn && <>
                    <div {...getRootProps()} className="w-full h-32 border border-8 border-dashed rounded my-4 text-center flex justify-center flex-col text-neutral-500">
                        <input {...getInputProps()} />
                        <p>Drag and drop files here, or click to browse</p>
                        <ul>{files}</ul>
                    </div>
                    <button className="bg-sky-400" onClick={() => submitFiles()}>Translate</button>
                    {loading && <ReactLoading type="balls" color="#38BDF8" />}
                    {translated && <Link href="/history" className="hover:bg-blue-600 hover:underline px-2">Translated</Link>}
                </>}
                    {/* <h1 className="text-center text-5xl text-sky-500">TransLayout</h1> */}
                    <h2 className="my-4">About us</h2>
                    <p>Blah blah blah blah</p>
                    {!loggedIn && <Link href="/login"><button className="bg-sky-400">Sign in now</button></Link>}
                <ToastContainer />
            </main>
        </div>
    )


}
