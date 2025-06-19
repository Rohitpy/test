package com.sab.mdm.user.batch;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap; import java.util.HashSet;
import java.util. Hashtable;
import java.util.List; import java.util.UUID;
import java.util. concurrent.ConcurrentHashMap;
import javax.naming.Context;
import javax.naming.NamingEnumeration; import javax.naming.didectory.Attribute; import javax.naming.directory.Attributes;
import javax.naming.directory.SearchControls; import javax.naming.directory.SearchResult; import javax.naming. ldap.InitialLdapContext;
import javax.naming. ldap.LdapContext;
import org. hibernate Session;
import ong.hibernate.SessionFactonys import ong. s1f4j.MDC;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import com.sab.mdm.common.constants.CommonConstants;
import com.sab.mdm.persistence.dtos.CRUDObject;
import com.sab.mdm.persistence.json.services.JS0NPersistenceService;
import com.sab.mdm.security.services.CryptionService;
import com.sab.mdm.user.constants.UserConstants;
import com.sab.mdm.user.dtos.UserDto;
import com.sab.mdm.user.entites. LDAPUserAutoCreation;
import com.sab.mdm.user.entites.User;
import com.sab.mdm.user.entites.UserGroupMap;
import lombok.RequiredArgsConstructor;
import lombok.extern.s1f4j.S1f45;
@Component
@RequiredAngsConstructon
¿ConditionalOnPropenty (value = "security.ldap.auto,user,creation", havingValue - "true")
