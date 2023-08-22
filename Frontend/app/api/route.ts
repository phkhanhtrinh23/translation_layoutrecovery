import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    const body = await req.formData();
    console.log(req.body);
    console.log(cookies().get("user_id"));
    let formData = new FormData();
    formData.append('user_id', String(cookies().get("user_id").value));
    formData.append('file', body.get("file"));
    formData.append("language", "en");
    const res = await fetch(HOST+'/create', {
        method: "POST",
        body: formData
    });
    const data = await res.json()

    // let formData2 = new FormData();
    // formData.append("file_input", data.data.pdf_id);
    // formData.append("language", "vi");
    const res2 = await fetch(HOST+'/translation', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file_input: data.data.pdf_id,
            language: "vi"
        })
    })
    const data2 = res2.json();
    return NextResponse.json(data2);
}