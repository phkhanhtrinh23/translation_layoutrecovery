import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    console.log(cookies().get("user_id"));
    let formData = new FormData();
    formData.append('user_id', String(cookies().get("user_id")));
    formData.append('file', String(req.body));
    formData.append("language", "en");
    const res = await fetch(HOST+'/create', {
        body: formData
    });
    const data = await res.json()
    return NextResponse.json(data);
}