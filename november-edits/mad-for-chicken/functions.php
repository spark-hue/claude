<?php
/**
 * Mad For Chicken theme.
 * The front page prints parts/site.html (the approved design) with asset paths pointed at this theme.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

/* Where each form is delivered. Change an address here to reroute that form. */
function mfc_form_recipients() {
	return array(
		'franchise' => 'franchise@madforchickenusa.com',
		'contact'   => 'support@madforchickenusa.com',
		'club'      => 'support@madforchickenusa.com', // Mad Club sign-ups; move to the email platform later
	);
}

add_action( 'after_setup_theme', function () {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
} );

/** Each page of the design and its real address. Same URLs the old site used, so search rankings carry over. */
function mfc_routes() {
	return array(
		'home'      => '/',
		'madness'   => '/process/',
		'menu'      => '/menu/',
		'locations' => '/locations/',
		'events'    => '/events/',
		'contact'   => '/contact/',
		'franchise' => '/franchise/',
	);
}

/** Which page of the design this request is for ('home', 'menu'…), or null for anything else (Terms, single events…). */
function mfc_current_view() {
	static $view = false;
	if ( false !== $view ) { return $view; }
	$path = trim( (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH ), '/' );
	$base = trim( (string) wp_parse_url( home_url( '/' ), PHP_URL_PATH ), '/' );
	if ( $base && 0 === strpos( $path, $base ) ) { $path = trim( substr( $path, strlen( $base ) ), '/' ); }
	$view = null;
	foreach ( mfc_routes() as $name => $route ) {
		if ( trim( $route, '/' ) === $path ) { $view = $name; break; }
	}
	return $view;
}

/** The built design, with assets resolved to the theme folder. */
function mfc_site_html() {
	static $html = null;
	if ( null === $html ) {
		$html = (string) file_get_contents( get_theme_file_path( 'parts/site.html' ) );
		$html = str_replace( 'assets/', trailingslashit( get_theme_file_uri() ) . 'assets/', $html );
	}
	return $html;
}

/** One block of the built design, e.g. the site header or footer, for the inner-page template. */
function mfc_site_part( $pattern ) {
	return preg_match( $pattern, mfc_site_html(), $m ) ? $m[0] : '';
}

/** Point in-page links (#menu, #locations…) at the homepage when used on inner pages. */
function mfc_home_links( $html ) {
	$html = mfc_route_links( $html );
	return preg_replace( '/href="#([a-z][\w-]*)"/', 'href="' . esc_url( home_url( '/' ) ) . '#$1"', $html );
}

/** Swap the build's #page links (and #top) for the pages' real addresses. */
function mfc_route_links( $html ) {
	foreach ( mfc_routes() as $name => $route ) {
		$url  = esc_url( home_url( $route ) );
		$html = str_replace( 'href="#' . $name . '"', 'href="' . $url . '"', $html );
	}
	return str_replace( 'href="#top"', 'href="' . esc_url( home_url( '/' ) ) . '"', $html );
}

/* ---------- The homepage is always the approved design.
   Page builders (e.g. Elementor Canvas / Full Width) swap in their own template for the front page;
   this runs last so the theme's front-page.php wins. ---------- */
add_filter( 'template_include', function ( $template ) {
	if ( is_front_page() || null !== mfc_current_view() ) {
		$ours = get_theme_file_path( 'front-page.php' );
		if ( file_exists( $ours ) ) { return $ours; }
	}
	return $template;
}, PHP_INT_MAX );

/* ---------- Inner pages (Careers, Terms, Privacy…) use the theme's page template, not a page-builder one. ---------- */
add_filter( 'template_include', function ( $template ) {
	if ( is_page() && ! is_front_page() && null === mfc_current_view() ) {
		$ours = get_theme_file_path( 'page.php' );
		if ( file_exists( $ours ) ) { return $ours; }
	}
	return $template;
}, PHP_INT_MAX );

/* Elementor Pro: the theme draws its own header and footer, so don't let site-wide Elementor templates replace them. */
add_action( 'elementor/theme/register_locations', function ( $manager ) {
	if ( method_exists( $manager, 'register_all_core_location' ) ) { $manager->register_all_core_location(); }
} );

/* Elementor's page and kit CSS isn't used by this theme and would restyle its headings, so keep it off the front end. */
add_action( 'wp_enqueue_scripts', function () {
	if ( isset( $_GET['elementor-preview'] ) ) { return; }
	global $wp_styles;
	foreach ( (array) $wp_styles->queue as $h ) { if ( false !== stripos( $h, 'elementor' ) ) { wp_dequeue_style( $h ); } }
}, 10000 );
add_filter( 'body_class', function ( $classes ) {
	return array_values( array_filter( $classes, function ( $c ) { return 0 !== strpos( $c, 'elementor-kit-' ); } ) );
} );

/** Title with the brand's swash capital on each capitalised word (as in the rest of the site). */
function mfc_swash( $title ) {
	$words = preg_split( '/\s+/', wp_strip_all_tags( $title ) );
	$out   = array();
	foreach ( $words as $w ) {
		$first = mb_substr( $w, 0, 1 );
		$out[] = ( $first !== mb_strtolower( $first ) ) ? '<i>' . esc_html( $first ) . '</i>' . esc_html( mb_substr( $w, 1 ) ) : esc_html( $w );
	}
	return implode( ' ', $out );
}

/**
 * Page content shown in the site's own typography: keep headings, text, lists, links and images,
 * drop page-builder wrappers, dead "#" buttons, and a leading heading that just repeats the page title.
 */
function mfc_clean_content( $html, $title ) {
	$allowed = array(
		'h2' => array(), 'h3' => array(), 'h4' => array(), 'h5' => array(), 'h6' => array(),
		'p' => array(), 'br' => array(), 'hr' => array(), 'blockquote' => array(),
		'ul' => array(), 'ol' => array(), 'li' => array(),
		'strong' => array(), 'b' => array(), 'em' => array(), 'i' => array(),
		'a' => array( 'href' => true, 'target' => true, 'rel' => true ),
		'img' => array( 'src' => true, 'alt' => true, 'width' => true, 'height' => true ),
		'table' => array(), 'thead' => array(), 'tbody' => array(), 'tr' => array(), 'th' => array(), 'td' => array(),
	);
	$html = preg_replace( '/<h1\b[^>]*>(.*?)<\/h1>/is', '<h2>$1</h2>', $html );
	$html = wp_kses( $html, $allowed );
	$html = preg_replace( '/<a href="(#|)"[^>]*>.*?<\/a>/is', '', $html );       // buttons that go nowhere
	$html = preg_replace( '/<(p|h[2-6]|li)>\s*<\/\1>/i', '', $html );          // empty blocks
	$html = preg_replace( '/\n\s*\n+/', "\n", $html );
	$first = '/^\s*<h[2-6]>\s*' . preg_quote( wp_strip_all_tags( $title ), '/' ) . '\s*<\/h[2-6]>/i';
	return trim( preg_replace( $first, '', $html, 1 ) );
}

/* ---------- Leftover addresses -> their real pages (301) ---------- */
add_action( 'template_redirect', function () {
	if ( is_admin() ) { return; }
	$path = trim( (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH ), '/' );
	$map  = array(
		'madness'           => '/process/',
		'franshise-inquiry' => '/franchise/',
		'franchise-inquiry' => '/franchise/',
	);
	if ( isset( $map[ $path ] ) ) {
		wp_redirect( home_url( $map[ $path ] ), 301 );
		exit;
	}
} );

/* ---------- Keep other plugins' front-end CSS/JS off the homepage so it renders exactly as designed.
   Analytics/stats scripts and the admin bar are kept. ---------- */
add_action( 'wp_enqueue_scripts', function () {
	if ( ! is_front_page() && null === mfc_current_view() ) { return; }
	global $wp_styles, $wp_scripts;
	$keep = '/(admin-bar|dashicons|stats|gtag|google|site-kit|analytics|tag-manager|bilmur|jetpack-stats)/i';
	foreach ( (array) $wp_styles->queue as $h ) { if ( ! preg_match( $keep, $h ) ) { wp_dequeue_style( $h ); } }
	foreach ( (array) $wp_scripts->queue as $h ) { if ( ! preg_match( $keep, $h ) ) { wp_dequeue_script( $h ); } }
}, 9999 );
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );

/* ---------- Events: render the board rows from The Events Calendar ---------- */
function mfc_events_rows() {
	if ( ! function_exists( 'tribe_get_events' ) ) { return null; }
	$events = tribe_get_events( array( 'posts_per_page' => 20, 'ends_after' => 'now', 'orderby' => 'event_date', 'order' => 'ASC' ) );
	$out = '';
	foreach ( $events as $e ) {
		$start = tribe_get_start_date( $e, false, 'Y-m-d H:i:s' );
		$end   = tribe_get_end_date( $e, false, 'Y-m-d H:i:s' );
		$ts    = strtotime( $start );
		$cats  = get_the_terms( $e->ID, 'tribe_events_cat' );
		$cat   = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
		$cost  = function_exists( 'tribe_get_cost' ) ? tribe_get_cost( $e->ID, true ) : '';
		$desc  = $e->post_excerpt ? $e->post_excerpt : wp_trim_words( wp_strip_all_tags( $e->post_content ), 30 );
		$time  = strtolower( date( 'g:i a', $ts ) ) . ' – ' . strtolower( date( 'g:i a', strtotime( $end ) ) );
		$out  .= sprintf(
			'<div class="ev" role="listitem" data-start="%1$s" data-end="%2$s"><div><div class="ev__date"><b>%3$s</b><span>%4$s</span></div><span class="ev__dow">%5$s</span></div><div><span class="ev__cat">%6$s</span><h3>%7$s</h3><p>%8$s</p></div><div class="ev__time">%9$s<small>%10$s</small></div><a class="btn" href="%11$s" target="_blank" rel="noopener">Find out more <span class="arr">→</span></a></div>',
			esc_attr( $start ), esc_attr( $end ), esc_html( date( 'd', $ts ) ), esc_html( date( 'M', $ts ) ), esc_html( date( 'l', $ts ) ),
			esc_html( $cat ), esc_html( get_the_title( $e ) ), esc_html( $desc ), esc_html( $time ), esc_html( $cost ), esc_url( get_permalink( $e ) )
		);
	}
	return $out;
}

/* ---------- Forms: Contact, Request Info (franchise), Mad Club -> email ---------- */
function mfc_handle_form() {
	$subjects = array(
		'franchise' => 'Franchise Form Inquiry',
		'contact'   => 'Contact Form Inquiry',
		'club'      => 'Mad Club Sign-Up',
	);
	$type = isset( $_POST['form'] ) ? sanitize_key( wp_unslash( $_POST['form'] ) ) : '';
	if ( ! isset( $subjects[ $type ] ) ) { wp_send_json_error( 'bad form', 400 ); }
	if ( ! empty( $_POST['website'] ) ) { wp_send_json_success(); } // honeypot: quietly ignore bots

	// simple flood guard: 5 submissions per IP per 10 minutes
	$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : 'x';
	$key = 'mfc_form_' . md5( $ip );
	$n   = (int) get_transient( $key );
	if ( $n >= 5 ) { wp_send_json_error( 'slow down', 429 ); }
	set_transient( $key, $n + 1, 10 * MINUTE_IN_SECONDS );

	$raw    = isset( $_POST['fields'] ) ? json_decode( wp_unslash( $_POST['fields'] ), true ) : array();
	$lines  = array();
	$reply  = '';
	foreach ( (array) $raw as $pair ) {
		if ( ! is_array( $pair ) || count( $pair ) < 2 ) { continue; }
		$label = sanitize_text_field( $pair[0] );
		$value = sanitize_textarea_field( $pair[1] );
		if ( '' === $label ) { continue; }
		if ( ! $reply && is_email( $value ) ) { $reply = $value; }
		$lines[] = $label . ': ' . ( '' === $value ? '—' : $value );
	}
	if ( ! $reply ) { wp_send_json_error( 'email required', 400 ); }

	$body  = $subjects[ $type ] . "\n\n" . implode( "\n", $lines ) . "\n\n";
	$body .= 'Sent ' . wp_date( 'F j, Y g:i a' ) . ' from ' . home_url( '/' );
	$headers = array( 'Reply-To: ' . $reply );
	$to   = mfc_form_recipients();
	$sent = wp_mail( $to[ $type ], $subjects[ $type ], $body, $headers );
	$sent ? wp_send_json_success() : wp_send_json_error( 'mail failed', 500 );
}
add_action( 'wp_ajax_mfc_form', 'mfc_handle_form' );
add_action( 'wp_ajax_nopriv_mfc_form', 'mfc_handle_form' );

/**
 * Google Tag Manager (GTM-TDQQMKWW), requested by MFC: Franchise page only.
 * The site switches pages in place, so site.html gives the Franchise page a full page load
 * (in and out) to make sure this code runs, and only runs, on that page.
 */
function mfc_is_franchise_view() {
	return function_exists( 'mfc_current_view' ) && 'franchise' === mfc_current_view();
}
add_action( 'wp_head', function () {
	if ( ! mfc_is_franchise_view() ) { return; } ?>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-TDQQMKWW');</script>
<!-- End Google Tag Manager -->
<?php
}, 1 );
add_action( 'wp_footer', function () {
	if ( ! mfc_is_franchise_view() ) { return; } ?>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-TDQQMKWW"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<?php
}, 1 );

/**
 * Google Tag Manager (GTM-WXPM537S): the site's original container.
 * Runs on every page EXCEPT the Franchise page (which has its own GTM-TDQQMKWW above).
 */
add_action( 'wp_head', function () {
	if ( mfc_is_franchise_view() ) { return; } ?>
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-WXPM537S"></script>
<script>
 window.dataLayer = window.dataLayer || [];
 function gtag(){dataLayer.push(arguments);}
 gtag('js', new Date());
</script>
<?php
}, 1 );

/** Menu FAQ schema (FAQPage). Prints only on /menu/. Keep in sync with the Menu FAQs section in parts/site.html. */
add_action( 'wp_head', function () {
	if ( ! function_exists( 'mfc_current_view' ) || 'menu' !== mfc_current_view() ) { return; } ?>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Does Mad For Chicken have vegetarian options?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, we are proud to offer vegetarian chicken as part of our chicken wing lineup. Almost all of our fries are vegetarian, and we have a veggie bowl option as well."
      }
    },
    {
      "@type": "Question",
      "name": "Do you have vegan options?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, a few of our side dishes are vegan, including the edamame, guacamole & chips, and cajun fries."
      }
    },
    {
      "@type": "Question",
      "name": "Is Mad For Chicken kid-friendly?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, our restaurants are kid-friendly with a kids menu including a bulgogi or chicken bowl and mac and cheese."
      }
    },
    {
      "@type": "Question",
      "name": "Can you order Mad For Chicken online?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, we offer online ordering. Select your <a href=\"https://madforchicken.com/locations/\">location</a> to order takeout from your nearest Mad For Chicken. We also offer delivery services on various food delivery apps."
      }
    },
    {
      "@type": "Question",
      "name": "Can you make a reservation at Mad For Chicken?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We don’t take reservations at our restaurants."
      }
    },
    {
      "@type": "Question",
      "name": "How spicy are the sauces?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We have a variety of sauces ranging from mild or no spice, to very spicy. If you’re not interested in spice, soy garlic and garlic parmesan are safe picks. For our spiciest sauces, go with either spicy buldak or mango habanero."
      }
    },
    {
      "@type": "Question",
      "name": "Does Mad For Chicken only have chicken wings?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No, we offer our signature twice-fried, hand-sauced, and made to order chicken as wings, drumsticks, thighs, tenders, or even vegetarian chicken."
      }
    }
  ]
}
</script>
<?php
} );
