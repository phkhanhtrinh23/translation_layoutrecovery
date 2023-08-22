import Link from "next/link"
export default function Navbar() {
    return (
        <nav className="flex flex-col h-full bg-neutral-50 w-1/4 drop-shadow-xl">
            <h1 className="m-4 text-sky-500">TransLayout</h1>
            <ul className="h-full">
                <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/">Main page</Link></li>
                <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/files">Files</Link></li>
                <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/profile">Profile</Link></li>
                <li className="hover:bg-sky-50 p-4 text-lg font-semibold"><Link href="/login">Sign in</Link></li>
            </ul>
            <p className="p-4"><b>Pro tip:</b> You can sign in to save your translated documents for later editing</p>            
        </nav>
    )
}