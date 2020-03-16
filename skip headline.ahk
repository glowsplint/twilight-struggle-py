#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Sleep 1500

; Creates a new game
Send, new
sleep 50
Send, {Enter}
sleep 50

; Sets basic USSR influence configuration
Send, m 16 17 17 17 17 20
sleep 50
Send, {Enter}
sleep 50

; Sets basic US influence configuration
Send, m 15 15 15 15 12 12 12
sleep 50
Send, {Enter}
sleep 50

; Sets US handicap both to Iran
Send, m 30 30
sleep 50
Send, {Enter}
sleep 50

; Headlines 1-Asia Scoring for USSR
;Send, m 1
;sleep 50
;Send, {Enter}
;sleep 50

; Headlines 2-Europe Scoring for US
;Send, m 2
;sleep 50
;Send, {Enter}
;sleep 50


;s::
;ExitApp
;Return