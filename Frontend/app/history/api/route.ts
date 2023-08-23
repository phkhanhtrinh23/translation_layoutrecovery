import HOST from "@/app/components/config";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const res = await fetch(HOST+'/history/'+String(cookies().get("username").value));
    const data = await res.json()
    console.log(data)
    return NextResponse.json({...data, loggedIn: req.cookies.has("user_id")});
}

export async function POST(req: NextRequest) {
    const body = await req.json();
    let res;
    if (body.query==="")
        res = await fetch(HOST+'/pdf/'+String(cookies().get("username").value+"?type=all"));
    else 
        res = await fetch(HOST+'/pdf/'+String(cookies().get("username").value+"?type=search&query="+body.query));
    const data = await res.json()
    console.log(data);
    return NextResponse.json(data)
}