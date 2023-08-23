import HOST from "@/app/components/config";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const res = await fetch(HOST + '/user/' + String(cookies().get("username").value), { method: "POST" });
  const data = await res.json()
  return NextResponse.json({ ...data, loggedIn: req.cookies.has("user_id") });
}

export async function POST(req: Request) {
  const body = await req.formData();
  const res = await fetch(HOST + '/updateprofile/' + String(cookies().get("username").value), {
    method: 'POST',
    body: body
  });
  const data = await res.json()
  return NextResponse.json(data);
}