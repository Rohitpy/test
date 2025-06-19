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
public class UserCreationProcessTrigger {
private final CryptionService cys;
eValue ("${app.default.user}")
private String user;
@Value("S{security.ldap.ur1}")
private String ldapUrl;
@Value ("$(secuirty.ldap.manager-dn}")
private String managerDn;
@Value("$(security.ldap.manager-password}")
private String managerPassword;
@Value ("$(security.1dap.user-filter)")
private String userFilter;
EValue("S(security. ldap.user-base)")
private String userBase;
@Value("$(secuinty.ldap.user-dn}")
private String userDn;
@Value ("$(app.enable.ldap)")
private boolean enableLdap;
eValue("${security.ldap.group-filter]")
private String groupfilter;
private final SessionFactory sessionFactory; private final JSONPersistenceService jbs;

@Scheduled(fixedRate = 600000)
public void executeTask) {
log. info("Checking for new users if any");
if (lenableLdap)
return;
try (Session session = sessionFactory-openSession) {
SecurityContextHolder -getContext().setAuthentication(new UsernamePasswordAuthenticationToken(
UserDto. builder () id(user).build(), null, Collections.emptyList));
MDC. put (CommonConstants .APP_URL, "**);
MDC. put (CommonConstants-TRACKING_NUMBER, UUID. randomUID(). toString®);
MDC. put (CommonConstants.USER_ID, user);
List‹User> users = session.createNativeQuery (UserConstants. GET_ACTIVE_USERS, User.class) list();
ConcurrentHashMap<String, User> userMap = new ConcurrentHashMap<>©; users-parallelStream(). forEach(k -> ( userMap. put (k.getId(), k) ;
7) :
userMap. remove (user) ;
List<LDAPUserAutoCreation> ldapDetails = session
•createNativeQuery (UserConstants.GET_LDAP_DETAILS, LDAPUserAutoCreation.class).list();

Hashtable<String, String> environment = new Hashtable‹String, String>(); environment.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
environment.put(Context.PROVIDER_URL, 1dapUr1);
environment.put (Context.SECURITY_AUTHENTICATION, "simple");
environment.put (Context SECURITY_PRINCIPAL, managerDn) ;
environment.put (Context.SECURITY_CREDENTIALS, cys.decrypt(managerPassword));
HashMap<String, Boolean> alreadyProcessed = new HashMap<>);
LdapContext context = new InitialLdapContext(environment, null);
CRUDObject crObjUser = CRUDObject. builder (). tableName("User") -phyTableName ("US_MST_USER_PROFILE"). build();
CRUDObject crObjUG = CRUDObject. builder (). tableName("UserUGRelation") -phyTableName("US_MST_USER_GROUP_MAP")
-build();
List<HashMap<String, String>> dataUser = Collections
•synchronizedList(new ArrayList<HashMap<String, String>>0);
crobjUser.setData (dataUser);
I
List<HashMap<String, String>> dataUGDel = Collections
•synchronizedList(new ArrayList<HashMap<String, String>>O);
List<HashMap<String, String>> dataUGAdd = Collections
•synchronizedList(new ArrayList<HashMap<String, String>>);

try {
for (int i = 0; i ‹ ldapDetails.size(); i++) {
LDAPUserAutoCreation ldap = ldapDetails.get(i);
HashSet<String> currGrpUsrList = new HashSet>;
List<UserGroupMap> ugUsersList = new ArrayList<>);
HashSet<String> existingUsersUg = new HashSet<>();
ugUsersList = session.createNativeQuery(UserConstants.USER_UG_RELATION, UserGroupMap.class)
• setParameter (1, Idap. getGroupName()) list();
ugUsersList.stream().forEach(user -> t
existingUsersUg.add(user.getUserId();
}) ;
String searchFilter = String format("(&(objectclass=group) (cn=%s))", 1dap-getGroupName);
String searchBase = Idap.getSearchBase (
SearchControls searchControls = new SearchControls);
searchControls.setSearchScope(SearchControls.SUBTREE_SCOPE); searchControls.setReturningAttributes (new String[] { "member" }) ;
NamingEnumeration<SearchResult> results = context.search(searchBase,
searchFilter, searchControls);
if (results.hasMore)) €
SearchResult result = results.next();
Attributes attrs = result. getAttributes();
Attribute members = attrs.get ("member");
if (members != null) {
  




