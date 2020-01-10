# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define scm_version 1_7R4
%define simple_version 1.7

Name:           rhino
Version:        1.7R4
Release:        4%{?dist}
Epoch:          0
Summary:        JavaScript for Java
License:        MPLv2.0

Source0:        https://github.com/mozilla/rhino/archive/Rhino%{scm_version}_RELEASE.zip

Source2:        %{name}.script

Patch0:         %{name}-build.patch
Patch1:         %{name}-1.7R3-crosslink.patch
Patch2:         %{name}-shell-manpage.patch
URL:            http://www.mozilla.org/rhino/
Group:          Development/Libraries/Java

BuildRequires:  ant
BuildRequires:  java-1.6.0-openjdk-devel >= 1:1.6.0.0
Requires:       jpackage-utils
Requires:       jline

BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

Obsoletes:      %{name}-manual <= %{epoch}:%{version}-%{release}

%description
Rhino is an open-source implementation of JavaScript written entirely
in Java. It is typically embedded into Java applications to provide
scripting to end users.

%package        demo
Summary:        Examples for %{name}
Group:          Development/Libraries/Java

%description    demo
Examples for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Documentation

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{name}-Rhino%{scm_version}_RELEASE
%patch0 -p1 -b .build
%patch1 -p1 -b .crosslink
%patch2 -p1 -b .manpage

# Fix build
%{__perl} -pi -e 's|.*<get.*src=.*>\n||' build.xml testsrc/build.xml toolsrc/org/mozilla/javascript/tools/debugger/build.xml xmlimplsrc/build.xml

# Fix manifest
%{__perl} -pi -e 's|^Class-Path:.*\n||g' src/manifest

# Add jpp release info to version
%{__perl} -pi -e 's|^implementation.version: Rhino .* release .* \${implementation.date}|implementation.version: Rhino %{version} release %{release} \${implementation.date}|' build.properties

%build
ant deepclean jar copy-all javadoc -Dno-xmlbeans=1

pushd examples

export CLASSPATH=../build/%{name}%{scm_version}/js.jar:$(build-classpath xmlbeans/xbean 2>/dev/null)
%{javac} *.java
%{jar} cvf ../build/%{name}%{scm_version}/%{name}-examples.jar *.class
popd

%install
%__rm -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}
%{__cp} -a build/%{name}%{scm_version}/js.jar %{buildroot}%{_javadir}/%{name}-%{simple_version}.jar
%{__cp} -a build/%{name}%{scm_version}/%{name}-examples.jar %{buildroot}%{_javadir}/%{name}-examples-%{simple_version}.jar
(cd %{buildroot}%{_javadir} && %{__ln_s} %{name}-%{simple_version}.jar js.jar;
                               %{__ln_s} %{name}-%{simple_version}.jar js-%{simple_version}.jar;
                               %{__ln_s} %{name}-%{simple_version}.jar %{name}.jar;)
(cd %{buildroot}%{_javadir} && %{__ln_s} %{name}-examples-%{simple_version}.jar %{name}-examples.jar)

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{simple_version}
%{__cp} -a build/%{name}%{scm_version}/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{simple_version}
(cd %{buildroot}%{_javadocdir} && %{__ln_s} %{name}-%{simple_version} %{name})

# man page
mkdir -p %{buildroot}%{_mandir}/man1/
install -m 644 build/%{name}%{scm_version}/man/%{name}.1 %{buildroot}%{_mandir}/man1/%{name}.1

## script
%__mkdir_p %{buildroot}%{_bindir}
%__install -m 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# examples
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
%{__cp} -a examples/* %{buildroot}%{_datadir}/%{name}

%clean
%__rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/*
%{_javadir}/*
%{_mandir}/man1/%{name}.1*
%doc LICENSE.txt

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/*

%changelog
* Tue Feb 02 2016 Elliott Baron <ebaron@redhat.com> - 0:1.7R4-4
- Add missing man page patch.
- Resolves: rhbz#1298084

* Tue Feb 02 2016 Elliott Baron <ebaron@redhat.com> - 0:1.7R4-3
- Add man page for Rhino shell.
- Add LICENSE.txt.
- Resolves: rhbz#1298084

* Fri Nov 06 2015 Severin Gehwolf <sgehwolf@redhat.com> - 0:1.7R4-2
- Preserve nicer backward compatibility by using same jar file
  names and symlink names as 1.7-0.7.r2 did.

* Thu Nov 05 2015 Severin Gehwolf <sgehwolf@redhat.com> - 0:1.7R4-1
- Rebase to rhino 1.7R4. Resolves RHBZ#1244351.

* Mon Jan 25 2010 Deepak Bhole <dbhole@redhat.com> - 0:1.7-0.7.r2.2
- Updated license field

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:1.7-0.7.r2.1
- Rebuilt for RHEL 6

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.7-0.7.r2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun May 31 2009 Toshio Kuratomi <toshio@fedoraproject.org> - 0:1.7-0.6.r2
- Update to rhino1_7R2
- Add patch from Steven Elliott to fix exception in the interpreter shell.

* Mon Apr 20 2009 Lillian Angel <langel@redhat.com> - 0:1.7-0.4.r2pre.1.1
- Added jpackage-utils requirement.
- Resolves: rhbz#496435

* Thu Mar 26 2009 Lillian Angel <langel@redhat.com> - 0:1.7-0.3.r2pre.1.1
- Updated rhino-build.patch
- License for treetable has been fixed. Re-included this code, and removed patch.
- Resolves: rhbz#457336

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.7-0.2.r2pre.1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 13 2009 Lillian Angel <langel@redhat.com> - 0:1.7-0.1.r2pre.1.1
- Upgraded to 1.7r2pre.
- Resolves: rhbz#485135

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.6-0.1.r5.1.3
- drop repotag
- fix license tag

* Thu Mar 15 2007 Matt Wringe <mwringe@redhat.com> 0:1.6-0.1.r5.1jpp.2
- Remove script from build as the debugging tool is disabled due to it 
  containing proprietary code from Sun.

* Wed Mar 07 2007 Deepak Bhole <dbhole@redhat.com> 0:1.6-0.1.r5.1jpp.1
- Upgrade to 1.6r5
- Change release per Fedora guidelines
- Disable dependency on xmlbeans (optional component, not in Fedora yet)
- Disable building of debugger tool, as it needs confidential code from Sun
- Remove post/postuns for javadoc and add the two dirs as %%doc

* Wed Jun 14 2006 Ralph Apel <r.apel@r-apel.de> 0:1.6-0.r2.2jpp
- Add bea-stax-api in order to build xmlimpl classes 

* Tue May 31 2006 Fernando Nasser <fnasser@redhat.com> 0:1.6-0.r2.1jpp
- Upgrade to RC2

* Mon Apr 24 2006 Fernando Nasser <fnasser@redhat.com> 0:1.6-0.r1.2jpp
- First JPP 1.7 build

* Thu Dec 02 2004 David Walluck <david@jpackage.org> 0:1.6-0.r1.1jpp
- 1_6R1
- add demo subpackage containing example code
- add jpp release info to implementation version
- add script to launch js shell
- build E4X implementation (Requires: xmlbeans)
- remove `Class-Path' from manifest

* Tue Aug 24 2004 Fernando Nasser <fnasser@redhat.com> - 0:1.5-1.R5.1jpp
- Update to 1.5R5.
- Rebuild with Ant 1.6.2

* Sat Jul 19 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.5-1.R4.1.1jpp
- Update to 1.5R4.1.
- Non-versioned javadoc dir symlink.

* Fri Apr 11 2003 David Walluck <davdi@anti-microsoft.org> 0:1.5-0.R4.2jpp
- remove build patches in favor of perl
- add epoch

* Sun Mar 30 2003 Ville Skyttä <ville.skytta at iki.fi> - 1.5-0.r4.1jpp
- Update to 1.5R4.
- Rebuild for JPackage 1.5.

* Wed May 08 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5-0.R3.1jpp
- 1.5R3
- versioned dir for javadoc

* Sun Mar 10 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5-0.R2.9jpp
- versioned compatibility symlink

* Mon Jan 21 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5-0.R2.8jpp
- section macro
- new release scheme

* Thu Jan 17 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5R2-7jpp
- spec cleanup
- changelog corrections

* Fri Jan 11 2002 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5R2-6jpp
- backward compatibility js.jar symlink
- used original swing exemples archive
- fixed javadoc empty package-list file
- no dependencies for manual and javadoc packages

* Sat Dec 1 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5R2-5jpp
- javadoc in javadoc package
- fixed offline build

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.5R2-4jpp
- changed extension --> jpp

* Sat Oct 6 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5R2-3jpp
- first unified release
- s/jPackage/JPackage
- corrected license to MPL

* Sat Sep 15 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5R2-2mdk
- spec cleanup
- standardized cvs references

* Thu Aug 31 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.5R2-1mdk
- first Mandrake release
