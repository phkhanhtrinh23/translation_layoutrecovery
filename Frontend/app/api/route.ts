import HOST from "@/app/components/config";
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: Request) {
}

export async function GET(req: NextRequest) {
    return NextResponse.json({ loggedIn: req.cookies.has("user_id") });
}

export async function DELETE(req: NextRequest) {
    cookies().delete("user_id");
    cookies().delete("username");
    return NextResponse.json({ loggedIn: req.cookies.has("user_id") });
}