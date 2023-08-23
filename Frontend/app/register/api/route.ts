import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    const body = await req.json();
    const res = await fetch(HOST + '/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    const data = await res.json()
    return NextResponse.json(data);
}