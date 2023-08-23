'use client';
import { useEffect, useState } from "react";
import Navbar from './components/navbar'
import { useDropzone } from 'react-dropzone';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Link from "next/link";
import ReactLoading from 'react-loading';
import HOST from "./components/config";

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
        if (acceptedFiles[0] === undefined) {
            toast("Empty file");
            return;
        }
        if (acceptedFiles[0].size / 1024 / 1024 > 50) {
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
                .then(data => fetch(HOST + '/translation', {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        file_input: data.data.pdf_id,
                        language: "vi"
                    })
                }))
                .then(res => res.json())
                .then(data => { toast(data.status); setLoading(false); setTranslated(true) });
        } catch (err) { toast("Internal error, try again"); setLoading(false); }
    }
    return (
        <div className="min-h-screen flex">
            <Navbar />
            <main className="p-4 w-full">
                {loggedIn && <>
                    <div {...getRootProps()} className="w-full h-32 border border-8 border-dashed rounded mt-4 text-center flex justify-center flex-col text-neutral-500">
                        <input {...getInputProps()} />
                        <p>Drag and drop files here, or click to browse</p>
                        <ul>{files}</ul>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                        <button className="bg-sky-400 h-fit" onClick={() => submitFiles()}>Translate</button>
                        {loading && <ReactLoading type="balls" color="#38BDF8" />}
                        {translated && <Link href="/history" className="hover:text-blue-600 hover:underline px-2">Translated</Link>}
                    </div>
                </>}
                {/* <h1 className="text-center text-5xl text-sky-500">TransLayout</h1> */}
                <div className="flex gap-8 md:flex-row flex-col">
                    <div>
                        <h2 className="my-2">Introduction</h2>
                        <p>This website ensures accurate translations from English to Vietnamese/Japanese and maintains the original file layouts.
                        </p>
                        <h2 className="my-2">Technology</h2>
                        <p>The core of our app is Neural Machine Translation (NMT) and Optical Character Recognition (OCR) technologies. envit5, Helsinki-NLP/opus-mt-en-jap, and PaddleOCR model are integrated for unparalleled results. This harmonization heightens translation accuracy and extends capabilities to image-based text, revolutionizing comprehension.
                        </p>
                        <p>Moreover, our web-app is underpinned by Django, PostgreSQL, NextJS, and TailwindCSS, creating a robust backend and an intuitive, user-centric interface.
                        </p>
                        <h2 className="my-2">How to use</h2>
                        <p>Engaging with our app involves three technical steps:
                        </p>
                        <ul>
                            <li><p>Step 1: Upload English PDFs.
                            </p></li>
                            <li><p>Step 2: Initiate translation with a single click.
                            </p></li>
                            <li><p>Step 3: Retrieve translated documents or review historical files through the "View Files" section.
                            </p></li>
                            {!loggedIn && <div className="text-center mt-4">
                                <Link href="/login"><button className="bg-sky-400 w-1/3">Sign in now</button></Link>
                            </div>}
                        </ul>
                    </div>
                    <div className="flex flex-col gap-2">
                        <img src="1711.07064.en.vi-01.png" alt="English original" width="600" />
                        <img src="1711.07064v4-01.png" alt="Vietnamese translated" width="600" />
                    </div>

                </div>


                <ToastContainer />
            </main>
        </div>
    )


}
