from fastapi_mail import MessageSchema, MessageType
from app.core.mail import fast_mail


async def send_otp_email(
    recipient: str,
    otp: str,
    purpose: str,
):
    message = MessageSchema(
        subject=f"Your {purpose} OTP",
        recipients=[recipient],
        body=f"""
        <h2>FastAPI Application</h2>

        <p>Your OTP for {purpose} is:</p>

        <h1>{otp}</h1>

        <p>This OTP will expire in 10 minutes.</p>

        <p>If you did not request this, please ignore this email.</p>
        """,
        subtype=MessageType.html,
    )

    await fast_mail.send_message(message)