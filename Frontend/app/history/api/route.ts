import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function GET() {
    const username = cookies().get("username")
    const res = await fetch(HOST+'/history/'+String(username.value));
    const data = await res.json()
    return NextResponse.json({...data, loggedIn: username!==undefined});
}
