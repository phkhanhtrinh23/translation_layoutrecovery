"use client";
import { useState, useEffect } from 'react';
import Navbar from "../components/navbar";
import InfiniteScroll from 'react-infinite-scroll-component';
import { redirect } from 'next/navigation';
import Cookies from "js-cookie";
const History = () => {
    const [pdfLinks, setPdfLinks] = useState([]);
    const [hasMore, setHasMore] = useState(true);

    useEffect(() => {        
        if (Cookies.get("user_id")===undefined) redirect('/login');
        fetch("/history/api")
        .then(res => res.json())
        .then(data => {
            if (!data.loggedIn) redirect("/login");
            setPdfLinks(data.data)
        })
    }, []);

    const loadMore = () => {
        // Simulate loading more PDF links
        // In a real scenario, you might fetch more links from S3
        setHasMore(hasMore); // Set to true if more links are available
    };
    return (
        <div className="h-screen flex">
            <Navbar />
            <main className="p-4 w-full overflow-y-scroll">
                <h2>History</h2>
                
                    <InfiniteScroll
                    dataLength={pdfLinks.length}
                    next={loadMore}
                    hasMore={hasMore}
                    loader={<p>Loading...</p>}
                    endMessage={<p>No more PDFs</p>}
                >
                    <table className="w-full text-center">
                    <tr>
                        <th>Input file</th>
                        <th>Output file</th>
                        <th>Status</th>
                        <th>Datetime</th>
                    </tr>
                    {pdfLinks.map((record, index) => {
                        const timestamp = record.time;
                        const [datePart, timePart] = timestamp.split("T")
                        const parsedDate = new Date(datePart + "T" + timePart);
                        const formattedDate = parsedDate.toISOString().replace("T", " ").slice(0, -5);
                        return (
                        <tr className="p-4">
                            <td>
                            <a href={record.file_input_url} target="_blank" rel="noopener noreferrer" className="hover:text-sky-600 hover:underline">
                            {record.file_input}
                            </a>
                            </td>
                            <td>
                            <a href={record.file_output_url} target="_blank" rel="noopener noreferrer" className="hover:text-sky-600 hover:underline">
                            {record.file_output}
                            </a>
                            </td>
                            <td>{record.status === 1 ? <span className="bg-green-600 text-white p-1 rounded-full">Successful</span> : 
                            (record.status === 0 ? <span className="bg-yellow-600 text-white p-1 rounded-full">Processing</span> : 
                            <span className="bg-red-600 text-white p-1 rounded-full">Unsuccessful</span>)}</td>
                            <td><span>{formattedDate}</span></td>
                            
                            </tr>
                    )})}
                    </table>
                </InfiniteScroll>
                
                
            </main>
        </div>
    )
}

export default History;