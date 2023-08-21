import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function GET() {
    const res = await fetch(HOST+'/user/'+cookies().get("username"));
    const data = await res.json()
    return NextResponse.json(data);
}

export async function POST(req: Request) {
    const res = await fetch(HOST+'/updateprofile/'+cookies().get("username"), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: req.body
      });
    const data = await res.json()
    return NextResponse.json(data);
}