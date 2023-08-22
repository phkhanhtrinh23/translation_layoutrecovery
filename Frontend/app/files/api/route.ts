import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function GET() {
    const username = cookies().get("username").value
    const res = await fetch(HOST+'/pdf/'+String(username+"?type=all"));
    const data = await res.json()
    return NextResponse.json(data);
}
