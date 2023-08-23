import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    const body = await req.json();
    const res = await fetch(HOST+'/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
    });
    const data = await res.json()
    if (data.status === "Logged in successfully") {
        cookies().set('user_id', data.data.user_id, { expires: Date.now() + 24 * 60 * 60 * 1000*7 });
        cookies().set('username', data.data.username, { expires: Date.now() + 24 * 60 * 60 * 1000*7 });
    }
    return NextResponse.json(data);
}