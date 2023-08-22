import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function GET() {
    const res = await fetch(HOST+'/user/'+String(cookies().get("username").value), {method: "POST"});
    const data = await res.json()
    return NextResponse.json(data);
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