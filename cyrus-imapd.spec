Name: cyrus-imapd
Version: 2.3.16
Release: 6%{?dist}

%define ssl_pem_file %{_sysconfdir}/pki/%{name}/%{name}.pem

# uid/gid reserved, see setup:/usr/share/doc/setup*/uidgid
%define uid 76
%define gid 76

%define _cyrususer cyrus
%define _cyrusgroup mail
%define _cyrexecdir %{_exec_prefix}/lib/%{name}

Summary: A high-performance mail server with IMAP, POP3, NNTP and SIEVE support
License: BSD
Group: System Environment/Daemons
URL: http://cyrusimap.web.cmu.edu/
Source0: ftp://ftp.andrew.cmu.edu/pub/cyrus/%{name}-%{version}.tar.gz
Source1: cyrus-imapd.logrotate
Source2: cyrus-imapd.imap-2.3.x-conf
Source3: cyrus-imapd.pam-config
Source4: http://email.uoa.gr/projects/cyrus/autocreate/README.autocreate-cyrus-2.3
Source5: http://email.uoa.gr/projects/cyrus/autosievefolder/README.autosievefolder
Source6: cyrus-imapd.init
Source7: cyrus-imapd.sysconfig
Source8: http://invoca.ch/pub/packages/cyrus-imapd/scripts/convertdb/cvt_cyrusdb_all
Source9: http://invoca.ch/pub/packages/cyrus-imapd/scripts/convertdb/magic
Source10: cyrus-imapd.cron-daily
Source11: README.rpm

# inclusion requested:
# https://bugzilla.andrew.cmu.edu/show_bug.cgi?id=3182
# https://bugzilla.andrew.cmu.edu/show_bug.cgi?id=3212
Patch1: http://email.uoa.gr/download/cyrus/cyrus-imapd-2.3.16/cyrus-imapd-2.3.16-autocreate-0.10-0.diff

# inclusion requested:
# https://bugzilla.andrew.cmu.edu/show_bug.cgi?id=3212
Patch2: http://email.uoa.gr/download/cyrus/cyrus-imapd-2.3.16/cyrus-imapd-2.3.16-autosieve-0.6.0.diff

Patch3: http://www.oakton.edu/~jwade/cyrus/cyrus-imapd-2.1.3/cyrus-imapd-2.1.3-flock.patch

Patch4: cyrus-imapd-2.3.1-authid_normalize.patch

# fedora/rhel specific, we use different directory
Patch5: cyrus-imapd-2.3.1-make_md5_defaults.patch

# fedora/rhel specific, find current db lib, rhbz#461875
Patch6: cyrus-imapd-2.3.12p2-current-db.patch

# temporary workaround, rhbz#553011, https://bugzilla.andrew.cmu.edu/show_bug.cgi?id=3206
Patch7: cyrus-imapd-2.3.16-nodenny.patch

# from upstream, rhbz#576652, for cyrus-imapd < 2.4
Patch8: cyrus-imapd-2.3.15-qos.patch

# fix man page
Patch9: cyrus-imapd-2.3.16-fixmanpage.patch

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires: autoconf
BuildRequires: cyrus-sasl-devel, perl-devel, tcp_wrappers
BuildRequires: db4-devel, openssl-devel, pkgconfig
BuildRequires: flex, bison, groff, automake
BuildRequires: openldap-devel
BuildRequires: krb5-devel
BuildRequires: net-snmp-devel
BuildRequires: transfig

Requires(post): e2fsprogs, chkconfig, initscripts, perl, grep, coreutils, findutils
Requires(preun): chkconfig, initscripts, coreutils
Requires(postun): initscripts

Requires: %{name}-utils = %{version}-%{release}
Requires: file, db4-utils
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description
The %{name} package contains the core of the Cyrus IMAP server.
It is a scaleable enterprise mail system designed for use from
small to large enterprise environments using standards-based
internet mail technologies.

A full Cyrus IMAP implementation allows a seamless mail and bulletin
board environment to be set up across multiple servers. It differs from
other IMAP server implementations in that it is run on "sealed"
servers, where users are not normally permitted to log in and have no
system account on the server. The mailbox database is stored in parts
of the file system that are private to the Cyrus IMAP server. All user
access to mail is through software using the IMAP, POP3 or KPOP
protocols. It also includes support for virtual domains, NNTP,
mailbox annotations, and much more. The private mailbox database design
gives the server large advantages in efficiency, scalability and
administratability. Multiple concurrent read/write connections to the
same mailbox are permitted. The server supports access control lists on
mailboxes and storage quotas on mailbox hierarchies.

The Cyrus IMAP server supports the IMAP4rev1 protocol described
in RFC 3501. IMAP4rev1 has been approved as a proposed standard.
It supports any authentication mechanism available from the SASL
library, imaps/pop3s/nntps (IMAP/POP3/NNTP encrypted using SSL and
TLSv1) can be used for security. The server supports single instance
store where possible when an email message is addressed to multiple
recipients, SIEVE provides server side email filtering.

%package devel
Group: Development/Libraries
Summary: Cyrus IMAP server development files

%description devel
The %{name}-devel package contains header files and libraries
necessary for developing applications which use the imclient library.

%package utils
Group: Applications/System
Summary: Cyrus IMAP server administration utilities
Requires(pre): shadow-utils
Requires(post): grep, coreutils, make, openssl
Requires(postun): shadow-utils
Obsoletes: %{name}-perl < 2.3.16-5

%description utils
The %{name}-utils package contains administrative tools for the
Cyrus IMAP server. It can be installed on systems other than the
one running the server.

%prep
%setup -q
%patch1 -p1 -b .autocreate
%patch2 -p1 -b .autosieve
%patch3 -p1 -b .flock
%patch4 -p1 -b .authid_normalize
%patch5 -p1 -b .make_md5_defaults
%patch6 -p1 -b .db4.7
%patch7 -p1 -b .nodenny
%patch8 -p1 -b .qos
%patch9 -p1 -b .fixmanpage

install -m 644 %{SOURCE4} %{SOURCE5} %{SOURCE11} doc/

# only to update config.* files
automake -a -f -c || :
aclocal -I cmulocal
autoheader
autoconf -f

# Modify docs master --> cyrus-master
%{__perl} -pi -e "s@master\(8\)@cyrus-master(8)@" man/*5 man/*8 lib/imapoptions
sed -i -e 's|\([^-]\)master|\1cyrus-master|g;s|^master|cyrus-master|g;s|Master|Cyrus-master|g;s|MASTER|CYRUS-MASTER|g' \
        man/master.8 doc/man.html

# Modify path in perl scripts
find . -type f -name "*.pl" | xargs %{__perl} -pi -e "s@/usr/local/bin/perl@%{__perl}@"

# modify lmtp socket path in .conf files
%{__perl} -pi -e "s@/var/imap/@%{_var}/lib/imap/@" master/conf/*.conf doc/cyrusv2.mc

# enable idled in .conf files to prevent error messages
%{__perl} -pi -e "s/#  idled/  idled/" master/conf/*.conf

# Fix permissions on perl programs
find . -type f -name "*.pl" -exec chmod 755 {} \;

%build
CPPFLAGS="$RPM_OPT_FLAGS -I%{_includedir}/et -I%{_includedir}/kerberosIV"; export CPPFLAGS
CFLAGS="$RPM_OPT_FLAGS -fPIC"; export CFLAGS
CCDLFLAGS="-rdynamic"; export CCDLFLAGS
%ifnarch ppc ppc64
LDFLAGS="$LDFLAGS -pie"; export LDFLAGS
%endif

%{configure} \
  --enable-netscapehack \
  --enable-listext \
  --enable-idled \
  --with-ldap=/usr \
  --with-snmp \
  --without-snmp \
  --enable-murder \
  --enable-replication \
  --enable-nntp \
  --with-perl=%{__perl} \
  --with-cyrus-prefix=%{_cyrexecdir} \
  --with-service-path=%{_cyrexecdir} \
  --with-bdb-incdir=%{_includedir}/db4 \
  --with-extraident="Fedora-RPM-%{version}-%{release}" \
  --with-syslogfacility=MAIL \
  --with-krbimpl=mit

make -C man -f Makefile.dist
make -C doc -f Makefile.dist
make
make -C notifyd notifytest

%install
rm -rf %{buildroot}

# This is needed to install the perl files correctly
pushd perl/imap
  %{__perl} Makefile.PL PREFIX=%{buildroot}%{_prefix} INSTALLDIRS=vendor
popd
pushd perl/sieve/managesieve
  %{__perl} Makefile.PL PREFIX=%{buildroot}%{_prefix} INSTALLDIRS=vendor
popd

# Do what the regular make install does
make install DESTDIR=%{buildroot} PREFIX=%{_prefix} mandir=%{_mandir}
make -C man install DESTDIR=%{buildroot} PREFIX=%{_prefix} mandir=%{_mandir}

install -m 755 imtest/imtest       %{buildroot}%{_bindir}/
install -m 755 notifyd/notifytest  %{buildroot}%{_bindir}/
install -m 755 perl/imap/cyradm    %{buildroot}%{_bindir}/

# Install tools
for tool in tools/* ; do
  test -f ${tool} && install -m 755 ${tool} %{buildroot}%{_cyrexecdir}/
done

# Create directories
install -d \
  %{buildroot}%{_sysconfdir}/{rc.d/init.d,logrotate.d,pam.d,sysconfig,cron.daily} \
  %{buildroot}%{_libdir}/sasl \
  %{buildroot}%{_var}/spool/imap \
  %{buildroot}%{_var}/lib/imap/{user,quota,proc,log,msg,socket,db,sieve,sync,md5,rpm,backup,meta} \
  %{buildroot}%{_var}/lib/imap/ptclient \
  %{buildroot}%{_datadir}/%{name}/rpm \
  %{buildroot}%{_sysconfdir}/pki/%{name} \
  doc/contrib

# Install additional files
install -m 755 %{SOURCE8}   %{buildroot}%{_cyrexecdir}/cvt_cyrusdb_all
install -m 644 %{SOURCE9}   %{buildroot}%{_datadir}/%{name}/rpm/magic
install -p -m 644 master/conf/prefork.conf %{buildroot}%{_sysconfdir}/cyrus.conf
install -p -m 644 %{SOURCE2}    %{buildroot}%{_sysconfdir}/imapd.conf
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/pop
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/imap
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/sieve
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/mupdate
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/lmtp
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/nntp
install -p -m 644 %{SOURCE3}    %{buildroot}%{_sysconfdir}/pam.d/csync
install -p -m 644 %{SOURCE1}    %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -m 755 %{SOURCE6}   %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
install -p -m 644 %{SOURCE7}   %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -p -m 755 %{SOURCE10}   %{buildroot}%{_sysconfdir}/cron.daily/%{name}

# Cleanup of doc dir
find doc perl -name CVS -type d -prune -exec rm -rf {} \;
find doc perl -name .cvsignore -type f -exec rm -f {} \;
rm -f doc/Makefile.dist*
rm -f doc/text/htmlstrip.c
rm -f doc/text/Makefile
rm -rf doc/man

# fix permissions on perl .so files
find %{buildroot}%{_libdir}/perl5/ -type f -name "*.so" -exec chmod 755 {} \;

# fix conflicts with uw-imap
mv %{buildroot}%{_mandir}/man8/imapd.8 %{buildroot}%{_mandir}/man8/imapd.8cyrus
mv %{buildroot}%{_mandir}/man8/pop3d.8 %{buildroot}%{_mandir}/man8/pop3d.8cyrus

# Install templates
install -m 755 -d doc/conf
install -m 644 master/conf/*.conf doc/conf/

# Generate db config file
( grep '^{' lib/imapoptions | grep _db | cut -d'"' -f 2,4 | \
  sed -e 's/^ *//' -e 's/-nosync//' -e 's/ *$//' -e 's/"/=/'
  echo sieve_version=2.2.3 ) | sort > %{buildroot}%{_datadir}/%{name}/rpm/db.cfg

# create the ghost pem file
touch %{buildroot}%{ssl_pem_file}

# Rename 'master' binary and manpage to avoid clash with postfix
mv -f %{buildroot}%{_cyrexecdir}/master         %{buildroot}%{_cyrexecdir}/cyrus-master
mv -f %{buildroot}%{_mandir}/man8/master.8      %{buildroot}%{_mandir}/man8/cyrus-master.8

# Rename 'fetchnews' binary and manpage to avoid clash with leafnode
mv -f %{buildroot}%{_cyrexecdir}/fetchnews      %{buildroot}%{_cyrexecdir}/cyrfetchnews
mv -f %{buildroot}%{_mandir}/man8/fetchnews.8   %{buildroot}%{_mandir}/man8/cyrfetchnews.8
%{__perl} -pi -e 's|fetchnews|cyrfetchnews|g;s|Fetchnews|Cyrfetchnews|g;s/FETCHNEWS/CYRFETCHNEWS/g' \
        %{buildroot}%{_mandir}/man8/cyrfetchnews.8

#remove executable bit from docs
for ddir in doc perl/imap/examples
do
  find $ddir -type f -exec chmod -x {} \;
done

# Remove installed but not packaged files
rm -f %{buildroot}%{_cyrexecdir}/not-mkdep
rm -f %{buildroot}%{_cyrexecdir}/config2header*
rm -f %{buildroot}%{_cyrexecdir}/config2man
rm -f %{buildroot}%{_cyrexecdir}/pop3proxyd
find %{buildroot} -name "perllocal.pod" -exec rm -f {} \;
find %{buildroot} -name ".packlist" -exec rm -f {} \;
rm -f %{buildroot}%{_mandir}/man8/syncnews.8*
find %{buildroot}%{perl_vendorarch} -name "*.bs" -exec rm -f {} \;

%clean
rm -rf %{buildroot}

%pre
# Create 'cyrus' user on target host
/usr/sbin/groupadd -g %{gid} -r saslauth 2> /dev/null || :
/usr/sbin/useradd -c "Cyrus IMAP Server" -d %{_var}/lib/imap -g %{_cyrusgroup} \
  -G saslauth -s /sbin/nologin -u %{uid} -r %{_cyrususer} 2> /dev/null || :

%post
/sbin/chkconfig --add %{name}

# Create SSL certificates
exec > /dev/null 2> /dev/null

if [ ! -f %{ssl_pem_file} ]; then
pushd %{_sysconfdir}/pki/tls/certs
umask 077
cat << EOF | make %{name}.pem
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
localhost.localdomain
root@localhost.localdomain
EOF
chown root.%{_cyrusgroup} %{name}.pem
chmod 640 %{name}.pem
mv %{name}.pem %{ssl_pem_file}
popd
fi

%preun
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi

%postun
if [ $1 != 0 ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc COPYRIGHT README
%doc doc/*
%config(noreplace) %{_sysconfdir}/cyrus.conf
%config(noreplace) %{_sysconfdir}/imapd.conf
%{_sysconfdir}/rc.d/init.d/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/pam.d/pop
%config(noreplace) %{_sysconfdir}/pam.d/imap
%config(noreplace) %{_sysconfdir}/pam.d/sieve
%config(noreplace) %{_sysconfdir}/pam.d/lmtp
%config(noreplace) %{_sysconfdir}/pam.d/mupdate
%config(noreplace) %{_sysconfdir}/pam.d/csync
%config(noreplace) %{_sysconfdir}/pam.d/nntp
%{_sysconfdir}/cron.daily/%{name}
%dir %{_cyrexecdir}
%{_cyrexecdir}/arbitron
%{_cyrexecdir}/arbitronsort.pl
%{_cyrexecdir}/chk_cyrus
%{_cyrexecdir}/convert-sieve.pl
%{_cyrexecdir}/cyr_df
%{_cyrexecdir}/ctl_cyrusdb
%{_cyrexecdir}/ctl_deliver
%{_cyrexecdir}/ctl_mboxlist
%{_cyrexecdir}/cvt_cyrusdb
%{_cyrexecdir}/cyr_dbtool
%{_cyrexecdir}/cyr_expire
%{_cyrexecdir}/cyr_synclog
%{_cyrexecdir}/cyrdump
%{_cyrexecdir}/cyrus-master
%{_cyrexecdir}/deliver
%{_cyrexecdir}/dohash
%{_cyrexecdir}/fud
%{_cyrexecdir}/imapd
%{_cyrexecdir}/ipurge
%{_cyrexecdir}/lmtpd
%{_cyrexecdir}/lmtpproxyd
%{_cyrexecdir}/make_sha1
%{_cyrexecdir}/masssievec
%{_cyrexecdir}/mbexamine
%{_cyrexecdir}/mbpath
%{_cyrexecdir}/migrate-metadata
%{_cyrexecdir}/mkimap
%{_cyrexecdir}/mknewsgroups
%{_cyrexecdir}/notifyd
%{_cyrexecdir}/pop3d
%{_cyrexecdir}/quota
%{_cyrexecdir}/reconstruct
%{_cyrexecdir}/rehash
%{_cyrexecdir}/sievec
%{_cyrexecdir}/sieved
%{_cyrexecdir}/smmapd
%{_cyrexecdir}/squatter
%{_cyrexecdir}/timsieved
%{_cyrexecdir}/tls_prune
%{_cyrexecdir}/translatesieve
%{_cyrexecdir}/undohash
%{_cyrexecdir}/unexpunge
%{_cyrexecdir}/upgradesieve
%{_cyrexecdir}/cvt_cyrusdb_all
%{_cyrexecdir}/idled
%{_cyrexecdir}/compile_sieve
%{_cyrexecdir}/mupdate
%{_cyrexecdir}/mupdate-loadgen.pl
%{_cyrexecdir}/proxyd
%{_cyrexecdir}/make_md5
%{_cyrexecdir}/sync_client
%{_cyrexecdir}/sync_reset
%{_cyrexecdir}/sync_server
%{_cyrexecdir}/cyrfetchnews
%{_cyrexecdir}/nntpd
%{_cyrexecdir}/ptdump
%{_cyrexecdir}/ptexpire
%{_cyrexecdir}/ptloader
%attr(0750,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/backup
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/db
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/log
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/meta
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/md5
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/msg
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %{_var}/lib/imap/proc
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %{_var}/lib/imap/ptclient
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/quota
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/rpm
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/sieve
%attr(0750,%{_cyrususer},%{_cyrusgroup}) %{_var}/lib/imap/socket
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/sync
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/lib/imap/user
%attr(0700,%{_cyrususer},%{_cyrusgroup}) %dir %{_var}/spool/imap
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/rpm
%{_datadir}/%{name}/rpm/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%dir %{_sysconfdir}/pki/%{name}
%attr(0640,root,%{_cyrusgroup}) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{ssl_pem_file}

%files devel
%defattr(0644,root,root,0755)
%{_includedir}/cyrus
%{_libdir}/lib*.a
%{_mandir}/man3/imclient.3*

%files utils
%defattr(-,root,root)
%doc perl/imap/README
%doc perl/imap/Changes
%doc perl/imap/examples
%{_bindir}/*
%dir %{perl_vendorarch}/Cyrus
%dir %{perl_vendorarch}/Cyrus/IMAP
%{perl_vendorarch}/Cyrus/IMAP/Admin.pm
%{perl_vendorarch}/Cyrus/IMAP/Shell.pm
%{perl_vendorarch}/Cyrus/IMAP/IMSP.pm
%{perl_vendorarch}/Cyrus/IMAP.pm
%dir %{perl_vendorarch}/Cyrus/SIEVE
%{perl_vendorarch}/Cyrus/SIEVE/managesieve.pm
%dir %{perl_vendorarch}/auto
%dir %{perl_vendorarch}/auto/Cyrus
%dir %{perl_vendorarch}/auto/Cyrus/IMAP
%{perl_vendorarch}/auto/Cyrus/IMAP/IMAP.so
%dir %{perl_vendorarch}/auto/Cyrus/SIEVE
%dir %{perl_vendorarch}/auto/Cyrus/SIEVE/managesieve
%{perl_vendorarch}/auto/Cyrus/SIEVE/managesieve/managesieve.so
%{_mandir}/man3/Cyrus::IMAP::Admin.3pm.gz
%{_mandir}/man3/Cyrus::IMAP::Shell.3pm.gz
%{_mandir}/man3/Cyrus::IMAP.3pm.gz
%{_mandir}/man3/Cyrus::IMAP::IMSP.3pm.gz
%{_mandir}/man3/Cyrus::SIEVE::managesieve.3pm.gz
%{_mandir}/man1/*

%changelog
* Thu Jun 10 2010 Michal Hlavinka <mhlavink@redhat.com> - 2.3.16-6
- fix man pages syntax

* Mon Jun 07 2010 Michal Hlavinka <mhlavink@redhat.com> - 2.3.16-5
- spec cleanup
- simplified packaging (merge -perl in -utils)
- remove obsoleted and/or unmaintained additional sources/patches
- remove long time not used files from the cvs/srpm
- update additional sources/patches from their upstream

* Tue Jun 01 2010 Marcela Maslanova <mmaslano@redhat.com> - 2.3.16-4
- Mass rebuild with perl-5.12.0

* Tue Apr 20 2010 Michal Hlavinka <mhlavink@redhat.com> - 2.3.16-3
- add support for QoS marked traffic (#576652)

* Thu Jan 14 2010 Michal Hlavinka <mhlavink@redhat.com> - 2.3.16-2
- ignore user_denny.db if missing (#553011)
- fix location of certificates in default imapd.conf

* Tue Dec 22 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.16-1
- updated to 2.3.16

* Fri Dec 04 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-10
- fix shell for daily cron job (#544182)

* Fri Dec 04 2009 Stepan Kasal <skasal@redhat.com> - 2.3.15-9
- rebuild against perl 5.10.1

* Thu Nov 26 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-8
- spec cleanup

* Tue Nov 24 2009 Michal Hlavinka <mhlaivnk@redhat.com> - 2.3.15-7
- rebuild with new db4 (#540093)
- spec cleanup

* Fri Nov 06 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-6
- fix sourcing of /etc/sysconfig/cyrus-imapd (#533320)

* Thu Nov 05 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-5
- do not fill logs with mail (de)compression messages (#528093)

* Thu Oct 29 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-4
- spec cleanup

* Fri Oct 09 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-3
- fix cyrus user shell for db import (#528126)

* Fri Sep 18 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-2
- make init script LSB-compliant (#523227)

* Fri Sep 18 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.15-1
- fix buffer overflow in cyrus sieve (CVE-2009-3235)

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> - 2.3.14-6
- use password-auth common PAM configuration instead of system-auth

* Mon Sep 07 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.14-5
- fix buffer overflow in cyrus sieve (#521010)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.3.14-4
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.14-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon May 25 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.14-2
- rebuild because of changed dependencies

* Thu Apr 02 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.14-1
- updated to 2.3.14

* Wed Apr 01 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.3.13-5
- fix unowned directory (#483336).

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.13-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 02 2009 Michal Hlavinka <mhlavink@rehdat.com> - 2.3.13-3
- fix directory ownership

* Wed Jan 21 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.13-2
- fix: #480138 - assertion failed: libcyr_cfg.c: cyrus_options[opt].opt == opt

* Tue Jan 13 2009 Michal Hlavinka <mhlavink@redhat.com> - 2.3.13-1
- updated to 2.3.13

* Fri Sep 26 2008 Dan Horák <dan[at]danny.cz - 2.3.12p2-3
- better fix for linking with recent db4.x

* Fri Sep 12 2008 Dan Horák <dan[at]danny.cz - 2.3.12p2-2
- fix linking with db4.7 (Resolves: #461875)
- patch cleanup

* Mon Sep  1 2008 Dan Horák <dan[at]danny.cz - 2.3.12p2-1
- update to new upstream version 2.3.12p2
- update patches

* Mon Sep  1 2008 Dan Horák <dan[at]danny.cz - 2.3.11-3
- refresh patches

* Sat May 31 2008 Dan Horák <dan[at]danny.cz - 2.3.11-2
- call automake to update config.* files and be buildable again on rawhide

* Tue Mar 25 2008 Tomas Janousek <tjanouse@redhat.com> - 2.3.11-1
- update to latest upstream
- (temporarily) dropped the rmquota+deletemailbox patch (doesn't apply)

* Wed Mar 19 2008 Rex Dieter <rdieter@fedoraproject.org> - 2.3.9-12
- cyrus-imapd conflicts with uw-imap (#222506)

* Tue Mar 18 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.3.9-11
- add Requires for versioned perl (libperl.so)

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.3.9-10
- Autorebuild for GCC 4.3

* Fri Feb 08 2008 Tomas Janousek <tjanouse@redhat.com> - 2.3.9-9
- don't run cronjob if cyrus-imapd has never been started (#418191)

* Tue Dec 04 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.9-8
- move certificate creation from -utils postinst to main package
- rebuild with newer openssl and openldap

* Sun Sep 23 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.9-7
- updated the getgrouplist patch
- fixed a few undeclared functions (and int to pointer conversions)

* Wed Aug 22 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.9-6
- update to latest upstream
- updated all patches from uoa and reenabled rmquota+deletemailbox

* Thu Aug 16 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.9-5.rc2
- update to latest upstream beta

* Tue Aug 14 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.9-4.rc1
- update to latest upstream beta
- temporarily dropped the rmquota+deletemailbox patch (doesn't apply)
- fixed to compile with newer glibc
- added the getgrouplist patch from RHEL-4, dropped groupcache patch
- dropped the allow_auth_plain patch
- buildrequire perl-devel

* Mon Jul 23 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.8-3.2
- removed the lm_sensors-devel dependency, since it's properly required in
  net-snmp-devel
- #248984 - cyrus-imapd.logrotate updated for rsyslog

* Mon Apr 23 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.8-3.1
- the -devel subpackage no longer requires the main one

* Wed Apr 11 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.8-3
- updated the no-bare-nl patch (#235569), thanks to Matthias Hensler

* Wed Apr 04 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.8-2
- fixed mboxlist backup rotation (#197054)

* Mon Mar 12 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.8-1
- update to latest upstream

* Wed Jan 24 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.7-8
- compile with kerberos support

* Wed Jan 24 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.7-7
- fixed Makefile typo (caused multiarch conflict)

* Mon Jan 08 2007 Tomas Janousek <tjanouse@redhat.com> - 2.3.7-6
- #218046: applied patches to compile with db4-4.5

* Tue Dec  5 2006 John Dennis <jdennis@redhat.com> - 2.3.7-5
- Resolves: bug# 218046: Cyrus-imapd in rawhide needs to be rebuilt
  against new snmp package

* Thu Oct 05 2006 Christian Iseli <Christian.Iseli@licr.org> 2.3.7-4
 - rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Mon Sep 18 2006 John Dennis <jdennis@redhat.com> - 2.3.7-3
- bump rev for rebuild

* Fri Aug 04 2006 Petr Rockai <prockai@redhat.com> - 2.3.7-2
- only buildrequire lm_sensors on i386 and x86_64, since it is not
  available elsewhere

* Sun Jul 23 2006 Petr Rockai <prockai@redhat.com> - 2.3.7-1
- update to latest upstream version, fixes a fair amount of issues
- forward-port the autocreate and rmquota patches (used latest
  upstream patches, those are for 2.3.3)

* Tue Jul 18 2006 Petr Rockai <prockai@redhat.com> - 2.3.1-3
- install perl modules into vendor_perl instead of site_perl
- change mode of perl .so files to 755 instead of 555
- update pam configuration to use include directive instead
  of deprecated pam_stack
- change prereq on cyrus-imapd-utils to requires

* Tue Jul 11 2006 Petr Rockai <prockai@redhat.com> - 2.3.1-2.99.test1
- address bunch of rpmlint errors and warnings
- rename perl-Cyrus to cyrus-imapd-perl to be consistent with rest
  of package (the cyrus modules are not part of cpan)
- added provides on cyrus-nntp and cyrus-murder (the functionality
  is part of main package now)
- removed generation of README.buildoptions
- the two above made it possible to get rid of most build-time parameter
  guessing from environment
- get rid of internal autoconf (iew)
- don't strip binaries, renders -debuginfo useless...
- remove prereq's in favour of newly added requires(...)

* Tue Feb 28 2006 John Dennis <jdennis@redhat.com> - 2.3.1-2
- bring up to Simon Matter's 2.3.1-2 release
- fix bug #173319, require cyrus-sasl-lib instead of cyrus-sasl
- fix bug #176470, hardcoded disttag

* Wed Jan 25 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-2
- add backend_sigsegv patch
- add replication_policycheck patch

* Mon Jan 23 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-1
- update to official autocreate and autosievefolder patches

* Thu Jan 19 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.18
- update rpm_set_permissions script
- add snmp support as build time option, disabled by default
  because it doesn't build on older distributions

* Wed Jan 18 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.15
- add make_md5 patch

* Mon Jan 16 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.13
- add autosievefolder patch
- add rmquota+deletemailbox patch
- change default path for make_md5, add md5 directory

* Fri Jan 13 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.10
- spec file cleanup
- add more cvt_cyrusdb_all fixes
- fix pre/post scripts
- fix requirements
- add patch to set Invoca RPM config defaults
- add sync directory used for replication
- add autocreate patch

* Thu Jan 12 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.8
- update cvt_cyrusdb_all script
- build db.cfg on the fly

* Thu Jan 05 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.5
- create ptclient directory if ldap enabled

* Wed Jan 04 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.4
- build without ldap support if openldap is linked against SASLv1

* Tue Jan 03 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.3
- fix ldap support

* Mon Jan 02 2006 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.2
- add openldap-devel to buildprereq, build with ldap support

* Wed Dec 21 2005 Simon Matter <simon.matter@invoca.ch> 2.3.1-0.1
- update to 2.3.1, officially called BETA-quality release

* Fri Dec 16 2005 Simon Matter <simon.matter@invoca.ch> 2.3.0-0.4
- add skiplist.py to contrib/
- port authid_normalize patch

* Thu Dec 15 2005 Simon Matter <simon.matter@invoca.ch> 2.3.0-0.3
- reintroduce subpackage utils, fix requirements
- move some utils to %%{_bindir}/

* Wed Dec 14 2005 Simon Matter <simon.matter@invoca.ch> 2.3.0-0.2
- integrate subpackages murder, nntp, replication, utils

* Tue Dec 13 2005 Simon Matter <simon.matter@invoca.ch> 2.3.0-0.1
- update to 2.3.0, officially called BETA-quality release
- add replication subpackage

* Fri Dec 09 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-15.1
- add missing automake to buildprereq
- change package description

* Tue Dec 06 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-15
- update cvt_cyrusdb_all script
- update autocreate patches

* Mon Dec 05 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-14
- update cvt_cyrusdb_all script

* Mon Nov 14 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-13
- add 64bit quota support backported from 2.3

* Fri Nov 11 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-12
- add quickstart/stop option to init script to bypass db import/export
- add authid_normalize patch
- add allow_auth_plain_proxying patch
- update gcc4 patch
- remove useless fdatasync patch
- add private autoconf used for build, remove autoconf dependency
- generate correct docs including man pages
- remove unneeded files from doc directory

* Fri Nov 04 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-11
- add mupdate thread-safe patch

* Mon Oct 24 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-9.4
- add spool patch, which is already fixed in CVS

* Tue Aug 30 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-9.2
- pull in CPPFLAGS and LDFLAGS from openssl's pkg-config data, if it exists

* Wed Aug 24 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-9.1
- add timsieved_reset_sasl_conn patch

* Mon Aug 22 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-9
- cosmetic changes in pre and post scripts

* Fri Aug 19 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-8
- add more pki dir fixes for inplace upgrades

* Thu Aug 18 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-7
- include requirement for Berkeley DB utils

* Thu Aug 18 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-6
- fix recovery problems with db4, which do not exist with db3
- fix logic for handling ssl certs
- remove initlog from init script

* Wed Aug 17 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-5
- add notifytest to the distribution
- add functionality to convert all berkeley databases to skiplist
  on shutdown and convert them back as needed on startup. This should
  solve the upgrade problems with Berkeley databases.

* Tue Aug 16 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-4.14
- add gcc4 patch
- determine and handle pki directory for openssl correctly
- add skiplist recovery docs
- add notify_sms patch

* Mon Jul 18 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-4.10
- update cvt_cyrusdb_all script
- update autocreate patches

* Fri Jul 15 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-4.9
- add patch to remove ACLs with invalid identifier
- update cvt_cyrusdb_all script

* Sat Jun 18 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-4.1
- update munge8bit patch

* Wed Jun 08 2005 Simon Matter <simon.matter@invoca.ch> 2.2.12-4
- updated seenstate patch

* Thu Jun 02 2005 Simon Matter <simon.matter@invoca.ch>
- removed nolinkimapspool patch, added singleinstancestore patch instead

* Thu Jun 02 2005 Simon Matter <simon.matter@invoca.ch>
- added nolinkimapspool patch
- fix debug_package macro, it was still being expanded,
  comments don't hide macro expansion
- change license field to BSD, its not exact BSD, but BSD is the closest

* Fri Apr 22 2005 John Dennis <jdennis@redhat.com> - 2.2.12-6.fc4
- the openssl package moved all its certs, CA, Makefile, etc. to /etc/pki
  now we are consistent with the openssl directory changes.

* Thu Apr 21 2005 John Dennis <jdennis@redhat.com> - 2.2.12-5.fc4
- we finally have a common directory, /etc/pki for certs, so create
  /etc/pki/cyrus-imapd and put the ssl pem file there. The /etc/cyrus-imapd
  location will not be used, this change supercedes that.

* Mon Apr 18 2005 John Dennis <jdennis@redhat.com> - 2.2.12-4.fc4
- fix bug #141479, move ssl pem file from /usr/share/ssl/certs to /etc/cyrus-imapd/cyrus-imapd.pem
- change license field to BSD, its not exact BSD, but BSD is the closest.

* Fri Apr 15 2005 John Dennis <jdennis@redhat.com> - 2.2.12-3.fc4
- fix release field to be single digit

* Fri Apr 15 2005 John Dennis <jdennis@redhat.com> - 2.2.12-1.2.fc4
- fix debug_package macro, it was still being expanded,
  comments don't hide macro expansion
- fix changelog chronological order
- fix bug 118832, cyrus-imapd is modifying /etc/services

* Mon Apr  4 2005 John Dennis <jdennis@redhat.com> - 2.2.12-1.1.fc4
- bring up to 2.2.12, includes security fix for CAN-2005-0546

* Mon Mar 07 2005 Simon Matter <simon.matter@invoca.ch>
- updated rmquota+deletemailbox patches

* Fri Mar  4 2005 John Dennis <jdennis@redhat.com> - 2.2.10-11.4.fc4
- fix gcc4 build problems

* Thu Mar  3 2005 John Dennis <jdennis@redhat.com> 2.2.10-11.3.fc4
- bump rev for build

* Mon Feb 14 2005 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.12
- updated autocreate and autosievefolder patches

* Fri Feb 11 2005 John Dennis <jdennis@redhat.com> - 2.2.10-11.2.fc4
- make _contribdir identical to Simon's,
  I had been getting burned by rpm's bizarre handling of macros in comments

* Thu Feb 10 2005 John Dennis <jdennis@redhat.com> - 2.2.10-11.1.fc4
- bring up to date with Simon Matter's 2.2.10-11 rpm

* Sat Feb 05 2005 Simon Matter <simon.matter@invoca.ch>
- updated autosievefolder patch

* Tue Feb 01 2005 Simon Matter <simon.matter@invoca.ch>
- remove special ownership and permissions from deliver
- enable deliver-wrapper per default
- enable OutlookExpress seenstate patch per default

* Wed Jan 19 2005 Simon Matter <simon.matter@invoca.ch>
- updated autocreate patch

* Fri Jan 14 2005 Simon Matter <simon.matter@invoca.ch>
- spec file cleanup

* Tue Jan 11 2005 Simon Matter <simon.matter@invoca.ch>
- updated autocreate patch

* Fri Jan 07 2005 Simon Matter <simon.matter@invoca.ch>
- moved contrib dir into doc, made scripts not executable

* Thu Jan 06 2005 Simon Matter <simon.matter@invoca.ch>
- added more fixes to the autocreate patch
- don't use %%_libdir for %%_cyrexecdir, it's a mess on x86_64
- don't use %%_libdir for symlinks
- remove %%_libdir pachtes
- change pam configs to work on x86_64
- changed default build option for IDLED to on
- changed rpm_set_permissions to honor partitions in /etc/imapd.conf

* Tue Jan 04 2005 Simon Matter <simon.matter@invoca.ch>
- updated autocreate patch

* Mon Dec 20 2004 Simon Matter <simon.matter@invoca.ch>
- remove idled docs when disabled, fixes RedHat's bug #142345

* Fri Dec 17 2004 Simon Matter <simon.matter@invoca.ch>
- removed allnumeric patch, not needed anymore
- made groupcache a compile time option
- rename nntp's pam service, fixes RedHat's bug #142672

* Thu Dec 16 2004 Simon Matter <simon.matter@invoca.ch>
- updated groupcache patch
- updated cvt_cyrusdb_all to use runuser instead of su if available
- added upd_groupcache tool

* Wed Dec 15 2004 Simon Matter <simon.matter@invoca.ch>
- added groupfile patch to help those using nss_ldap

* Thu Dec 02 2004 Simon Matter <simon.matter@invoca.ch>
- modified config directives and removed verify options

* Thu Dec  2 2004 John Dennis <jdennis@redhat.com> 2.2.10-3.devel
- fix bug #141673, dup of bug #141470
  Also make cyrus.conf noreplace in addition to imapd.conf
  Remove the verify overrides on the noreplace config files,
  we do want config file changes visible when verifying

* Wed Dec  1 2004 John Dennis <jdennis@redhat.com> 2.2.10-2.devel
- fix bug #141470, make imapd.conf a noreplace config file

* Wed Dec  1 2004 John Dennis <jdennis@redhat.com> 2.2.10-1.devel
- update to Simon Matter's 2.2.10 RPM,
  fixes bug #139382, 
  security advisories: CAN-2004-1011 CAN-2004-1012 CAN-2004-1013 CAN-2004-1015

* Wed Nov 24 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.10

* Tue Nov 23 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.9

* Fri Nov 19 2004 Simon Matter <simon.matter@invoca.ch>
- changed scripts to use runuser instead of su if available

* Thu Nov 18 2004 Simon Matter <simon.matter@invoca.ch>
- changed requirement for file >= 3.35-1 from BuildPrereq to
  Requires, fixes RedHat's bug #124991
- added acceptinvalidfrom patch to fix RedHat's bug #137705

* Mon Oct 4 2004 Dan Walsh <dwalsh@redhat.com> 2.2.6-2.FC3.6
- Change cyrus init scripts and cron job to use runuser instead of su

* Fri Aug  6 2004 John Dennis <jdennis@redhat.com> 2.2.6-2.FC3.5
- remove obsoletes tag, fixes bugs #127448, #129274

* Wed Aug  4 2004 John Dennis <jdennis@redhat.com>
- replace commas in release field with dots, bump build number

* Tue Aug 03 2004 Simon Matter <simon.matter@invoca.ch>
- fixed symlinks for x86_64, now uses the _libdir macro
  reported by John Dennis, fixes RedHat's bug #128964
- removed obsoletes tag, fixes RedHat's bugs #127448, #129274

* Mon Aug  2 2004 John Dennis <jdennis@redhat.com> 2.2.6-2,FC3,3
- fix bug #128964, lib symlinks wrong on x86_64

* Thu Jul 29 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.8

* Thu Jul 29 2004 Simon Matter <simon.matter@invoca.ch>
- updated autocreate and autosieve patches
- made authorization a compile time option
- added sieve-bc_eval patch

* Tue Jul 27 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.7
- modified autocreate patch or 2.2.7
- removed snmpargs patch which was needed for RedHat 6.2

* Tue Jul 13 2004 Simon Matter <simon.matter@invoca.ch>
- added mboxlist / mboxname patches from CVS

* Tue Jul 06 2004 Simon Matter <simon.matter@invoca.ch>
- updated rmquota+deletemailbox patch

* Sat Jul  3 2004 John Dennis <jdennis@redhat.com> - 2.2.6-2,FC3,1
- bring up to date with Simon Matter's latest upstream rpm 2.2.6-2
- comment out illegal tags Packager, Vendor, Distribution
  build for FC3

* Wed Jun 30 2004 Simon Matter <simon.matter@invoca.ch>
- added quota patches from CVS

* Fri Jun 25 2004 Simon Matter <simon.matter@invoca.ch>
- updated autocreate patch

* Fri Jun 18 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.6

* Fri Jun 11 2004 Simon Matter <simon.matter@invoca.ch>
- updated autocreate and autosieve patches

* Tue Jun 01 2004 Simon Matter <simon.matter@invoca.ch>
- updated autocreate, autosieve and rmquota patches
- fixed rmquota patch to build on gcc v3.3.x
- added lmtp_sieve patch

* Sat May 29 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.5

* Fri May 28 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.5 pre-release

* Mon May 24 2004 Simon Matter <simon.matter@invoca.ch>
- added hash patch to fix a sig11 problem
- added noncritical typo patch

* Fri May 21 2004 Simon Matter <simon.matter@invoca.ch>
- include OutlookExpress seenstate patch
- fixed allnumeric patch

* Thu May 20 2004 Simon Matter <simon.matter@invoca.ch>
- don't enable cyrus-imapd per default
- rename fetchnews to cyrfetchnews to avoid namespace conflicts with leafnode
- replace fetchnews with cyrfetchnews in man pages
- replace master with cyrus-master in man pages

* Tue May 18 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.4

* Fri Apr 30 2004 Simon Matter <simon.matter@invoca.ch>
- Don't provides: imap

* Wed Mar 17 2004 Simon Matter <simon.matter@invoca.ch>
- fix init script

* Thu Mar 04 2004 Simon Matter <simon.matter@invoca.ch>
- strip binaries

* Tue Mar 02 2004 Simon Matter <simon.matter@invoca.ch>
- add more SELinux fixes

* Wed Feb 25 2004 Simon Matter <simon.matter@invoca.ch>
- add makedepend to path, thank you Andreas Piesk for reporting it

* Mon Feb 23 2004 Dan Walsh <dwalsh@redhat.com>
- change su within init script to get input from /dev/null
  this prevents hang when running in SELinux
- don't use -fpie as default, it breaks different distributions

* Thu Feb 19 2004 Simon Matter <simon.matter@invoca.ch>
- merged in most changes from Karsten Hopp's RedHat package
- fixed permissions of files in contrib, thank you
  Edward Rudd for reporting it.
- modified snmp patch to make it build on RedHat 6.2 again

* Tue Feb 03 2004 Karsten Hopp <karsten@redhat.de>
- switch to Simon Matter's cyrus-imapd package, which has
  some major improvements over the old Red Hat package.
  - configdirectory moved from /var/imap to /var/lib/imap
  - sasl_pwcheck_method changed to saslauthd
- needed to delete package/vendor tags for buildsystem.
- added USEPIE variable for linking with -fpie flag
- removed rpath from linker arguments
- removed email header from README.HOWTO-recover-mailboxes
- added lib64 patch
- use CFLAGS from specfile in imtest subdir
- disable -pie on ppc for now

* Tue Feb 03 2004 Simon Matter <simon.matter@invoca.ch>
- added tls_ca_file: to imapd.conf
- updated autocreate patch which fixes a small sig11 problem

* Thu Jan 29 2004 Simon Matter <simon.matter@invoca.ch>
- convert sieve scripts to UTF-8 only if sievec failed before
- add note to the readme about limiting loggin on busy servers
- added build time option to chose the syslog facility

* Wed Jan 28 2004 Simon Matter <simon.matter@invoca.ch>
- sieve scripts are now converted to UTF-8 with cvt_cyrusdb_all

* Tue Jan 27 2004 Simon Matter <simon.matter@invoca.ch>
- fixed problems with masssievec
- lots of small fixes in the init scripts

* Fri Jan 23 2004 Simon Matter <simon.matter@invoca.ch>
- updated auto db converting functionality
- added auto masssievec functionality

* Thu Jan 22 2004 Simon Matter <simon.matter@invoca.ch>
- updated autocreate/autosievefolder patches

* Fri Jan 16 2004 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.3

* Wed Jan 14 2004 Simon Matter <simon.matter@invoca.ch>
- number of mailbox list dumps can now be configured

* Fri Jan 01 2004 Simon Matter <simon.matter@invoca.ch>
- updated autosievefolder patch

* Thu Dec 18 2003 Simon Matter <simon.matter@invoca.ch>
- updated autocreate/autosievefolder/rmquota patches

* Tue Oct 28 2003 Simon Matter <simon.matter@invoca.ch>
- updated to 2.2.2-BETA

* Tue Aug 05 2003 Simon Matter <simon.matter@invoca.ch>
- add sendmail m4 macro, some people were looking for it
- just one source for pam default configuration (they were all the same)
- added /etc/pam.d/lmtp
- added build support for RedHat Beta severn

* Wed Jul 30 2003 Simon Matter <simon.matter@invoca.ch>
- updated autocreate patch to 0.8.1
- removed creation of spool/config dirs, not needed anymore
- added cyrus_sharedbackup to contrib

* Fri Jul 18 2003 Simon Matter <simon.matter@invoca.ch>
- modified for 2.2.1-BETA

* Wed Jul 09 2003 Simon Matter <simon.matter@invoca.ch>
- modified rpm_set_permissions script

* Mon Jul 07 2003 Simon Matter <simon.matter@invoca.ch>
- changed permissions on config and spool dirs
- modified init script

* Thu Jul 03 2003 Simon Matter <simon.matter@invoca.ch>
- upgraded to 2.1.14
- removed now obsolete forcedowncase patch
- use --with-extraident to add extra version information
- updated munge8bit patch

* Wed Jun 04 2003 Simon Matter <simon.matter@invoca.ch>
- added RedHat 2.1ES support to the perlhack detection

* Tue May 20 2003 Simon Matter <simon.matter@invoca.ch>
- upgraded autocreate patch

* Fri May 09 2003 Simon Matter <simon.matter@invoca.ch>
- upgraded autocreate patch
- modified init script

* Mon May 05 2003 Simon Matter <simon.matter@invoca.ch>
- upgraded to 2.1.13
- replaced commands with macros, cleaned up spec file

* Fri May 02 2003 Simon Matter <simon.matter@invoca.ch>
- added murder subpackage
- changed exec path to /usr/lib/cyrus-imapd

* Thu May 01 2003 Simon Matter <simon.matter@invoca.ch>
- included modified munge8bit patch again

* Tue Apr 29 2003 Simon Matter <simon.matter@invoca.ch>
- added new 8bit header patch
- upgraded IPv6 patch
- upgraded autocreate patch to 0.7

* Mon Apr 28 2003 Simon Matter <simon.matter@invoca.ch>
- added new autocreate patch

* Mon Mar 31 2003 H-E Sandstrom <hes@mailcore.net>
- added munge8bit patch

* Mon Mar 24 2003 Simon Matter <simon.matter@invoca.ch>
- added createonpost fix patch

* Thu Mar 20 2003 Simon Matter <simon.matter@invoca.ch>
- added functionality to patch the IPv6 patch on the fly if
  autoconf > 2.13, we can now use newer autoconf again.

* Tue Mar 18 2003 Paul Bender <pbender@qualcomm.com>
- fixed spec file so that autoconf 2.13 will always be used,
  since the IPv6 patch requires autoconf <= 2.13

* Fri Mar 14 2003 Simon Matter <simon.matter@invoca.ch>
- fixed problems with new file package

* Thu Mar 13 2003 Simon Matter <simon.matter@invoca.ch>
- added kerberos include for RedHat Beta phoebe 2
- added Henrique's forcedowncase patch

* Mon Mar 03 2003 Simon Matter <simon.matter@invoca.ch>
- corrected imapd.conf

* Sat Mar 01 2003 Simon Matter <simon.matter@invoca.ch>
- added note about lmtp socket in sendmail
- added flock patches

* Fri Feb 07 2003 Simon Matter <simon.matter@invoca.ch>
- added build time option for fulldirhash

* Wed Feb 05 2003 Simon Matter <simon.matter@invoca.ch>
- added IPV6 patch to source rpm
- fixed build on RedHat 6.2

* Tue Feb 04 2003 Simon Matter <simon.matter@invoca.ch>
- update to 2.1.12
- added logrotate entry for /var/log/auth.log
- modified init script to use builtin daemon mode

* Fri Jan 10 2003 Simon Matter <simon.matter@invoca.ch>
- small change in mboxlist backup script

* Fri Jan 10 2003 Simon Matter <simon.matter@invoca.ch>
- fixed a cosmetic bug in cvt_cyrusdb_all
- added cron.daily job to backup mailboxes.db

* Mon Jan 06 2003 Simon Matter <simon.matter@invoca.ch>
- add more entries to /etc/services

* Wed Jan 01 2003 Simon Matter <simon.matter@invoca.ch>
- include snmpargs patch for build on RedHat 6.2
- added build support for RedHat 6.2

* Mon Dec 30 2002 Simon Matter <simon.matter@invoca.ch>
- removed autoconf hack, not needed anymore
- enabled build on RedHat Beta Phoebe
- added services entry for lmtp
- cleanup spec file

* Thu Dec 26 2002 Simon Matter <simon.matter@invoca.ch>
- removed BuildPrereq for e2fsprogs-devel

* Thu Dec 12 2002 Simon Matter <simon.matter@invoca.ch>
- modified RedHat release detection
- added BuildPrereq for file

* Thu Dec 05 2002 Simon Matter <simon.matter@invoca.ch>
- upgraded to cyrus-imapd 2.1.11
- upgrade IPV6 patch to 20021205

* Thu Nov 28 2002 Simon Matter <simon.matter@invoca.ch>
- Fixed some default attributes

* Thu Nov 28 2002 Troels Arvin <troels@arvin.dk>
- Explicitly changed files-section to
   - use defattr for simple (root-owned 0644) files
   - explictly set root as user/group owner where
     the user/group ownership was previously indicated
     as "-"; this allows building valid packages without
     having to being root when building

* Mon Nov 25 2002 Simon Matter <simon.matter@invoca.ch>
- changed default build option for IDLED to off
- included some useful info in README.*

* Thu Nov 21 2002 Simon Matter <simon.matter@invoca.ch>
- added build time option for IDLED, thank you Roland Pope

* Tue Nov 19 2002 Simon Matter <simon.matter@invoca.ch>
- fixed spec to really use fdatasync patch
- added createonpost patch

* Thu Nov 14 2002 Simon Matter <simon.matter@invoca.ch>
- upgraded to cyrus-imapd 2.1.10
- build without IPv6 support by default

* Tue Nov 12 2002 Simon Matter <simon.matter@invoca.ch>
- fixed db detection in .spec

* Mon Oct 21 2002 Simon Matter <simon.matter@invoca.ch>
- updated cvt_cyrusdb_all script

* Fri Oct 18 2002 Simon Matter <simon.matter@invoca.ch>
- added fdatasync patch

* Thu Oct 03 2002 Simon Matter <simon.matter@invoca.ch>
- add RPM version 4.1 compatibility, which means remove installed
  but not packaged files

* Wed Sep 18 2002 Simon Matter <simix@datacomm.ch>
- added auto db converting functionality
- changed default for MBOXLIST_DB and SEEN_DB to skiplist

* Mon Sep 16 2002 Simon Matter <simix@datacomm.ch>
- remove creation of cyrus user at build time
- added scripts from ftp://kalamazoolinux.org/pub/projects/awilliam/cyrus/

* Mon Sep 02 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.9

* Fri Aug 30 2002 Simon Matter <simix@datacomm.ch>
- included extra ident string

* Thu Aug 29 2002 Simon Matter <simix@datacomm.ch>
- modified path in deliver-wrapper, thank you Richard L. Phipps
- added RedHat 2.1AS support to the perlhack detection
- added build time option to force syncronous updates on ext3

* Wed Aug 28 2002 Simon Matter <simix@datacomm.ch>
- added updated IPv6 patch from Hajimu UMEMOTO

* Wed Aug 28 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.8

* Thu Aug 22 2002 Simon Matter <simix@datacomm.ch>
- included IPv6 patch from Hajimu UMEMOTO

* Wed Aug 21 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.7 because of wrong version info

* Wed Aug 21 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.6

* Mon Aug 19 2002 Simon Matter <simix@datacomm.ch>
- change db version detection, thank you Chris for reporting

* Tue Aug 13 2002 Simon Matter <simix@datacomm.ch>
- fixed autoconf detection

* Mon Aug 12 2002 Simon Matter <simix@datacomm.ch>
- included support for different autoconf versions
- modified the perl build and install process
- made some .spec changes to build on RedHat 7.x and limbo

* Fri Aug 09 2002 Simon Matter <simix@datacomm.ch>
- included sieve matching patch

* Thu Jun 27 2002 Simon Matter <simix@datacomm.ch>
- fixed %%post script where %%F was expanded to file.file

* Wed Jun 26 2002 Simon Matter <simix@datacomm.ch>
- fixed missing man page

* Tue Jun 25 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.5

* Mon Jun 24 2002 Simon Matter <simix@datacomm.ch>
- added compile time parameters to configure the package based on
  the idea from Luca Olivetti <luca@olivetti.cjb.net>
- make deliver-wrapper a compile time option

* Fri May 02 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.4

* Mon Apr 22 2002 Simon Matter <simix@datacomm.ch>
- small initscript fix

* Fri Mar 08 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.3
- removed some stuff that was cleaned up in the sources
- added compile time options for db backends

* Wed Mar 06 2002 Simon Matter <simix@datacomm.ch>
- removed requires perl-File-Temp for utils package, it's in the RedHat
  perl RPM now

* Fri Feb 22 2002 Simon Matter <simix@datacomm.ch>
- removed deliverdb/db

* Wed Feb 20 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.2

* Mon Feb 11 2002 Simon Matter <simix@datacomm.ch>
- changed sasl_mech_list: PLAIN in /etc/imapd.conf
- added sieve to /etc/pam.d

* Fri Feb 08 2002 Simon Matter <simix@datacomm.ch>
- added requires perl-File-Temp for utils package

* Wed Feb 06 2002 Simon Matter <simix@datacomm.ch>
- added some %%dir flags
- removed /usr/lib/sasl/Cyrus.conf
- added conf templates
- build time option for usage of saslauth group

* Tue Feb 05 2002 Simon Matter <simix@datacomm.ch>
- upgraded to cyrus-imapd 2.1.1
- dependency of cyrus-sasl >= 2.1.0-1

* Sun Feb 03 2002 Simon Matter <simix@datacomm.ch>
- saslauth group is only deleted on uninstall if there is no other
  member in this group

* Sat Feb 02 2002 Simon Matter <simix@datacomm.ch>
- changed start/stop level in init file

* Tue Jan 29 2002 Simon Matter <simix@datacomm.ch>
- dependency of cyrus-sasl >= 1.5.24-22
- dotstuffing patch for sendmail calls made by sieve for outgoing
  mails
- patch for ability to force ipurge to traverse personal folders

* Mon Jan 28 2002 Simon Matter <simix@datacomm.ch>
- minor spec file changes

* Sat Jan 19 2002 Simon Matter <simix@datacomm.ch>
- changed default auth to pam
- remove several %%dir from %%files sections
- change from /usr/lib/cyrus -> /usr/libexec/cyrus
- rename source files to something like cyrus...
- added rehash tool
- changed to hashed spool

* Fri Jan 18 2002 Simon Matter <simix@datacomm.ch>
- fixed init script
- fixed %%post section in spec

* Thu Jan 17 2002 Simon Matter <simix@datacomm.ch>
- ready for first build

* Wed Jan 09 2002 Simon Matter <simix@datacomm.ch>
- initial package, with help from other packages out there
