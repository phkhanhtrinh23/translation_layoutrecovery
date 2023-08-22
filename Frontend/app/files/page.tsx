"use client";
import { useState, useEffect } from 'react';
import Navbar from "../components/navbar";
import InfiniteScroll from 'react-infinite-scroll-component';

const Files = () => {
    const [pdfLinks, setPdfLinks] = useState([]);
    const [hasMore, setHasMore] = useState(true);

    useEffect(() => {
        // Simulate fetching PDF links from S3
        //fetch("https://d7d2-35-91-115-21.ngrok-free.app/")
        const fetchedPdfLinks = ['https://storage.googleapis.com/avatar-a0439.appspot.com/sample.pdf', 
        '/link1.pdf', '/link2.pdf', '/link3.pdf', /* ... */
        fetch("/files/api")
        .then(res => res.json())
        .then(data => setPdfLinks(data.data))
    ];
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
                <h2>Files</h2>
                <InfiniteScroll
                    dataLength={pdfLinks.length}
                    next={loadMore}
                    hasMore={hasMore}
                    loader={<p>Loading...</p>}
                    endMessage={<p>No more PDFs</p>}
                >
                    {pdfLinks.map((pdfLink, index) => {
                        const name = pdfLink.file.match(/\/([^/]+)$/)[1]
                        return (
                        <div key={index} className="p-4 border-b">
                            <a href={pdfLink.file} target="_blank" rel="noopener noreferrer" className="hover:text-sky-600 hover:underline">
                            {name}
                            </a>
                        </div>
                    )})}
                </InfiniteScroll>
            </main>
        </div>
    )
}

export default Files;