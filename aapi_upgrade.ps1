#! /bin/pwsh

# (c) 2020 - 2022 Daniel Companeetz, BMC Software, Inc.
# All rights reserved.

# BSD 3-Clause Licenses

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# SPDX-License-Identifier: BSD-3-Clause
# For information on SDPX, https://spdx.org/licenses/BSD-3-Clause.html

param ([int] $myversion=9, [int] $myrelease=20, [int] $fix)
#NOTE: Do not forget to change the versions

# Comment next line if no debug information is required
Set-PSDebug -Trace 1

#From <https://www.red-gate.com/simple-talk/sysadmin/powershell/how-to-use-parameters-in-powershell/>
param ( [int] $myversion, [int] $myrelease, [int] $fix)

# This is to run as see if the user isLocalAdmin
If($isWindows) {
    $outpath = $env:TEMP+"\padev_current.exe"
    $thisOS = "Windows"
    $thisArch="windows_x86_64"
    $thisExt=".exe"
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if(-Not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        write-host "This needs to be executed by an administrator. Exiting (rc=99)."
        exit 99
    }
}

#No validation if Linux. Assumes it is the EM User
If($isLinux) {
    $outpath = "/tmp/padev_current.exe"
    $thisOS = "Unix"
    $thisArch="Linux-x86_64"
    $thisExt="_INSTALL.BIN"
}

if ($fix -eq $null) {
    write-host "Please enter a fix pack. Assuming $myversion.$myrelease. Exiting (rc=42)."
    exit 42
} else {
    $fixpack = $fix.PadLeft(3,'0')
    $file_to_download="PADEV.$myversion.0.$myrelease.$fixpack"+"_"+$thisArch+$thisExt
    $url = "https://controlm-appdev.s3-us-west-2.amazonaws.com/release/v"+$myversion+"."+$myrelease+"."+$fix+"/output/"+$thisOS+"/"+$file_to_download
        #https://controlm-appdev.s3-us-west-2.amazonaws.com/release/v9.21.5/output/Windows/PADEV.9.0.20.005_windows_x86_64.exe
    write-host "Downloading from $url"
    Invoke-WebRequest -Uri $url -OutFile $outpath -SkipCertificateCheck
    write-host "Downloaded from $url"
    chmod 755 $outpath
    write-host "Starting installation of $outpath"
    Start-Process -Wait -Filepath "$outpath" -ArgumentList "-s -v"
    write-host "Completed installation of $outpath"
}
# Debuggone
Set-PSDebug -Trace 0
exit 0
