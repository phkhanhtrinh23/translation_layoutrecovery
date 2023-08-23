import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: Request) {
    const body = await req.formData();
    let formData = new FormData();
    formData.append('user_id', cookies().get("user_id").value);
    formData.append('file', body.get("file"));
    formData.append("language", "en");
    const res = await fetch(HOST + '/create', {
        method: "POST",
        body: formData,
    });
    const data = await res.json()
    return NextResponse.json(data);
}

export async function GET(req: NextRequest) {
    return NextResponse.json({ loggedIn: req.cookies.has("user_id") });
}

export async function DELETE(req: NextRequest) {
    cookies().delete("user_id");
    cookies().delete("username");
    return NextResponse.json({ loggedIn: req.cookies.has("user_id") });
}