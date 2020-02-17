#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Sleep 3000

Send, m a
sleep 100
Send, {Enter}
sleep 100
Send, m y
sleep 100
Send, {Enter}
sleep 100
Send, m fi
sleep 100
Send, {Enter}
sleep 100
Send, m y
sleep 100
Send, {Enter}
sleep 100

loop, 2
{
Send, m fi
sleep 100
Send, {Enter}
sleep 100
}

Send, m y
sleep 100
Send, {Enter}

s::
ExitApp
Return