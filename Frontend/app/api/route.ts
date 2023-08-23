import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: Request) {
    // const body = await req.formData();
    // body.append('user_id', cookies().get("user_id").value);
    // body.append("language", "en");
    // console.log(body.get("file"));
    // const res = await fetch(HOST + '/create', {
    //     method: 'POST',
    //     body: body,
    // });

    // const data = await res.json()

    // const res2 = await fetch(HOST + '/translation', {
    //     method: "POST",
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({
    //         file_input: data.data.pdf_id,
    //         language: "vi"
    //     })
    // })
    // const data2 = res2.json();
    // return NextResponse.json(data2);

}

export async function GET(req: NextRequest) {
    return NextResponse.json({ loggedIn: req.cookies.has("user_id") });
}

export async function DELETE(req: NextRequest) {
    cookies().delete("user_id");
    cookies().delete("username");
    return NextResponse.json({ loggedIn: req.cookies.has("user_id") });
}