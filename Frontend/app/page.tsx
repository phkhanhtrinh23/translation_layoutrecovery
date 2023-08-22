'use client';
import { useEffect, useState } from "react";
import Navbar from './components/navbar'
import { useDropzone } from 'react-dropzone';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Cookies from 'js-cookie';
import { redirect } from 'next/navigation'
import HOST from "./components/config";
import { totalmem } from "os";


export default function Home() {
    const { acceptedFiles, getRootProps, getInputProps } = useDropzone();
    const [pdfLink, setPdfLink] = useState(null);
    const files = acceptedFiles.map(file => (
        <li key={file.path}>{file.path}</li>
    ));
    const submitFiles = async () => {
        const storedUserID = Cookies.get("user_id");
        console.log(storedUserID);
        if (storedUserID === undefined) {
            toast("Login");
            redirect("/login");
            return;
        }
        if (acceptedFiles[0] === undefined) {
            toast("Empty file");
            return;
        }
        try {
            const formData = new FormData();
            formData.append("file", acceptedFiles[0]);
            fetch("/api", {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then (data => {toast(data); setPdfLink(data.data.file_output)});
        } catch (err) { toast(err); }

    }
    return (
        <div className="h-screen flex">
            <Navbar />
            <main className="p-4 w-full">
                <div {...getRootProps()} className="w-full h-32 border border-8 border-dashed rounded my-4 text-center flex justify-center flex-col text-neutral-500">
                    <input {...getInputProps()} />
                    <p>Drag and drop files here, or click to browse</p>
                    <ul>{files}</ul>
                </div>
                <button className="bg-sky-400" onClick={() => submitFiles()}>Translate</button>
                {pdfLink && <a href={pdfLink} target="_blank" rel="noopener noreferrer" className="hover:text-sky-600 hover:underline">Translated File</a>}
                <h2 className="my-4">About us</h2>
                <p>Blah blah blah blah</p>
                <ToastContainer />
            </main>
        </div>
    )


}
