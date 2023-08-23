
import Link from "next/link"
import { useEffect, useState } from "react"
export default function Navbar() {
    const [loggedIn, setLoggedIn] = useState(false);
    useEffect(() => {
        fetch("/api")
            .then(res => res.json())
            .then(data => setLoggedIn(data.loggedIn))
    }, [])
    const logout = () => {
        fetch("/api", { method: "DELETE" })
            .then(res => res.json())
            .then(data => setLoggedIn(data.loggedIn))
    }
    return (
        <nav className="flex flex-col min-h-screen bg-neutral-50 w-1/4 drop-shadow-xl">
            <h1 className="m-4 text-sky-500">TransLayout</h1>
            <ul className="h-full">
                <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/">Home</Link></li>
                {loggedIn ? <>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/history">History</Link></li>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/profile">Profile</Link></li>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><a href="/" onClick={() => logout()}>Logout</a></li>
                </> : <>
                    <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/login">Sign in</Link></li>
                </>}
            </ul>
            <p className="p-4"><b>Pro tip:</b> You can sign in to save your translated documents for later editing</p>
        </nav>
    )
}