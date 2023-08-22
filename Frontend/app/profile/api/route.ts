import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function GET() {
    const username = cookies().get("username");
    if (username===undefined) return NextResponse.json({loggedIn: false});
    const res = await fetch(HOST+'/user/'+String(username.value), {method: "POST"});
    const data = await res.json()
    return NextResponse.json({...data, loggedIn: true});
}

export async function POST(req: Request) {
  const body = await req.json();
    const res = await fetch(HOST+'/updateprofile/'+String(cookies().get("username").value), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: body
      });
    const data = await res.json()
    return NextResponse.json(data);
}