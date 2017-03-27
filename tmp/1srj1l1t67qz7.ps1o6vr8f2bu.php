<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
	<meta property="og:image" content="https://map.arquivista.net/etc/mapa.png" />
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
	<meta name="description" content="The Open and Collaborative Archives World Map, a public archives geolocalization dataset.">
	<meta name="keywords" content="archives, map, collaborative, open">
	<meta name="author" content="Ricardo Sodré Andrade">
	<link rel="shortcut icon" href="https://map.arquivista.net/etc/templates/favicon.ico">


    <title>Archives World Map</title>

    <!-- Bootstrap core CSS -->
    <link href="https://map.arquivista.net/etc/bootstrap-3.3.7-dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="https://map.arquivista.net/etc/bootstrap-3.3.7-dist/css/starter-template.css" rel="stylesheet">

	<!-- Leaflet -->
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.3/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.0.3/dist/leaflet.js"></script>
	
	<!-- reCaptcha -->
	<script src='https://www.google.com/recaptcha/api.js'></script>
	
	<!-- Awesomplete css -->
	<link rel="stylesheet" href="https://map.arquivista.net/etc/awesomplete/awesomplete.css" />
	
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->

	 <script>
		  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
		  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
		  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

		  ga('create', 'UA-91391022-1', 'auto');
		  ga('send', 'pageview');
	</script> 
	  
  </head>

  <body>

    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="https://map.arquivista.net">Archives World Map</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="https://map.arquivista.net/"><?php echo $dict_home; ?></a></li>
            <li><a href="https://map.arquivista.net/add"><?php echo $dict_addarchives; ?></a></li>
			<li><a href="https://map.arquivista.net/search"><?php echo $dict_search; ?></a></li>
			<li><a href="https://map.arquivista.net/stats"><?php echo $dict_stats; ?></a></li>
            <li><a href="https://map.arquivista.net/about"><?php echo $dict_about; ?></a></li>
			<li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

    <div class="container">

      <div class="home">
	  <!-- Conteúdo oriundo do ff3 -->
	
		<?php if ($page=='mapa'): ?>
		
			<!-- Archives World Map home -->
			<!--<h1>Archives World Map</h1>
			<p class="lead"><?php echo $dict_theopenandcollaborative; ?></p>-->
<!--
<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<ins class="adsbygoogle"
     style="display:inline-block;width:320px;height:100px"
     data-ad-client="ca-pub-7782822980648918"
     data-ad-slot="1062084952"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script><br><hr>-->
			
			<p><a href="https://www.facebook.com/archivesworldmap/" target="_blank"><?php echo $dict_facebookcommunity; ?></a></p>
			<small><?php echo $dict_Languages; ?>: <a href="?language=en-US">English</a> | <a href="?language=es">Español</a> | <a href="?language=pt-BR">Português</a> | <a href="?language=cn">中文</a></small><br>
			<br>
			<div id="mapid" style="<?php echo $this->raw($sizemap); ?> margin: 0 auto"></div>
			<script>
 
				var mymap = L.map('mapid').setView([21.525484, -12.572412], 2);

				L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiYXJxdWl2aXN0YW5ldCIsImEiOiJjaXlwOXAzN2EwMDM0NDRwY3h0aG1yejB2In0.kGvUj7knV4iUH1OSnSqzdw', {
					maxZoom: 18,
					attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
					'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> | ' +
					'Archives geo and data &copy; <a href="https://map.arquivista.net">Archives World Map</a>',
					id: 'mapbox.streets'
				}).addTo(mymap);

				<?php echo $this->raw($pinagem); ?>

				
			</script>
		<?php endif; ?>
		<?php if ($page=='listmap' || $page=='listallmap'): ?>
			<p><a href="/logout">logout</a></p>
			<table width="95%">
			  <tr>
				<th width="8"><center>ID</th>
				<th width="55"><center><?php echo $dict_institution; ?></center></th>
				<th width="5"><center><?php echo $dict_archivescountry; ?></center></th>
				<th width="10"><center><?php echo $dict_archiveslatitude; ?></center></th>
				<th width="10"><center><?php echo $dict_archiveslongitude; ?></center></th>
				<th width="10"><center><?php echo $dict_map; ?></center></th>
				<th width="10"><center>Ações</th>
			  </tr>
			<?php foreach (($lista?:[]) as $item): ?>
			  <tr>
				<td><center><?php echo $item['id']; ?></center></td>
				<td><center><?php if ($item['status']=='waiting'): ?><b><?php endif; ?><?php echo $item['nome']; ?><?php if ($item['status']=='waiting'): ?></b><?php endif; ?></center></td>
				<td><center><?php echo $item['pais']; ?></center></td>
				<td><center><?php echo $item['latitude']; ?></center></td>
				<td><center><?php echo $item['longitude']; ?></center></td>
				<td><center><a href="http://maps.google.com/?q=<?php echo $item['latitude']; ?>,<?php echo $item['longitude']; ?>" target="_blank">Google Maps</a></center></td>
				<td><center><a href="./edit/<?php echo $item['id']; ?>">editar</a></center></td>
			  </tr>
			<?php endforeach; ?>
   
      </table>
      <br>
      <?php if ($page=='listallmap'): ?>
        <a href="https://map.arquivista.net/listall?since=<?php echo $back; ?>"><< Back</a>  - 
        <a href="https://map.arquivista.net/listall?since=<?php echo $forward; ?>">Forward >></a>
			<?php endif; ?>
		<?php endif; ?>
				
		<?php if ($page=='editmap'): ?>
		<?php foreach (($lista?:[]) as $item): ?>
		<form action="/proc-editmap/<?php echo $item['id']; ?>" method="POST">
		  <p>
		  <?php echo $dict_archivesname; ?><br>
		  <input type="text" name="nome" value="<?php echo $item['nome']; ?>" size="50" required>
		  <p>
		  <?php echo $dict_identifier; ?><br>
		  <input type="text" name="identificador" value="<?php echo $item['identificador']; ?>" size="50">
		  <p>
		  <?php echo $dict_archivesaddress; ?><br>
		  <input type="text" name="logradouro" value="<?php echo $item['logradouro']; ?>" size="50">
		  <p>
		  <?php echo $dict_archivescity; ?><br>
		  <input type="text" name="cidade" value="<?php echo $item['cidade']; ?>" size="50">
		  <p>
		  <?php echo $dict_archivesdistrict; ?><br>
		  <input type="text" name="estado" value="<?php echo $item['estado']; ?>" size="50">
		  <p>
		  <?php echo $dict_archivescountry; ?><br>
		  <input type="text" name="pais" value="<?php echo $item['pais']; ?>" size="50">
		  <p>
		  <?php echo $dict_archivesurl; ?><br>
		  <input type="url" name="url" value="<?php echo $item['url']; ?>" size="50">
		  <p>
		  <?php echo $dict_archivesemail; ?><br>
		  <input type="email" name="email" value="<?php echo $item['email']; ?>" size="50">
		  <p>
		  <?php echo $dict_archiveslatitude; ?><br>
		  <input type="text" name="latitude" value="<?php echo $item['latitude']; ?>" size="50" required>
		  <p>
		  <?php echo $dict_archiveslongitude; ?><br>
		  <input type="text" name="longitude" value="<?php echo $item['longitude']; ?>" size="50" required>
		  <br>
		  <br>
		  <?php echo $dict_archivesyourname; ?><br>
		  <input type="text" name="contributor" value="<?php echo $item['contributor']; ?>" size="50">
		  <br>
		  <?php echo $dict_archivesyouremail; ?><br>
		  <input type="text" name="contributoremail" value="<?php echo $item['contributoremail']; ?>" size="50">
		  <br>
		  <?php echo $dict_archivesstatus; ?><br>
		  <select name="status">
				<option value="waiting" <?php if ($item['status'] == 'waiting'): ?>selected<?php endif; ?>>Waiting</option>
				<option value="verified" <?php if ($item['status'] == 'verified'): ?>selected<?php endif; ?>>Verified</option>
		  </select>
		  <br>
		  <br>
		  <input type="submit" value="<?php echo $dict_sendtoinclusion; ?>">
		</form> 
		<p><a href="../del/<?php echo $item['id']; ?>">deletar registro</a>
		<?php endforeach; ?>
		<?php endif; ?>

		<?php if ($page=='infomap'): ?>
			<?php foreach (($lista?:[]) as $item): ?>
			
			<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
			<!-- Middle post -->
			<ins class="adsbygoogle"
				 style="display:block"
				 data-ad-client="ca-pub-7782822980648918"
				 data-ad-slot="4084570559"
				 data-ad-format="auto"></ins>
			<script>
			(adsbygoogle = window.adsbygoogle || []).push({});
			</script>
			<hr>
			<br>
			<div style="text-align: left;">
			<h2><?php echo $dict_infoarchives; ?></h2>
			<form>
			<p>
			  <?php echo $dict_institution; ?><br>
			  <input type="text" name="nome" value="<?php echo $this->raw($item['nome']); ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_identifier; ?><br>
			  <input type="text" name="identificador" value="<?php echo $item['identificador']; ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_archivesaddress; ?><br>
			  <input type="text" name="logradouro" value="<?php echo $item['logradouro']; ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_archivescity; ?><br>
			  <input type="text" name="cidade" value="<?php echo $item['cidade']; ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_archivesdistrict; ?><br>
			  <input type="text" name="estado" value="<?php echo $item['estado']; ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_archivescountry; ?><br>
			  <input type="text" name="pais" value="<?php echo $item['pais']; ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_archivesurl; ?><br>
			  <a href="<?php echo $item['url']; ?>" target="_blank"><?php echo $item['nome']; ?></a>
			  <p>
			  <?php echo $dict_archivesemail; ?> <br>
			  <input type="email" name="email" value="<?php echo $item['email']; ?>" readonly="readonly" size="35">
			  <p>
			  <?php echo $dict_location; ?>:<br>
			  [<a href="https://www.openstreetmap.org/?mlat=<?php echo $item['latitude']; ?>&mlon=<?php echo $item['longitude']; ?>#map=16/<?php echo $item['latitude']; ?>/<?php echo $item['longitude']; ?>" target="_blank">OpenStreetMap</a>] [<a href="http://maps.google.com/?q=<?php echo $item['latitude']; ?>,<?php echo $item['longitude']; ?>" target="_blank">Google Maps</a>] <br>
			  <p>
			  <?php echo $dict_collaborator; ?><br>
			  <input type="text" name="contributor" value="<?php echo $item['contributor']; ?>" readonly="readonly" size="35">
 
			</form> 
			</div>
			<?php endforeach; ?>
		<?php endif; ?>

		<?php if ($page=='addmap'): ?>
		<div style="text-align: left;">
			<h2><?php echo $dict_addarchives; ?></h2>
			<form action="/proc-addmap" method="POST">
			  <p>
			  <?php echo $dict_archivesname; ?>*<br><small><?php echo $this->raw($dict_nameauthorisedform); ?></small><br>
			  <input type="text" name="nome" value="" size="35" required>
			  <p>
			  <?php echo $dict_identifier; ?><br><small><?php echo $this->raw($dict_identifierform); ?></small><br>
			  <input type="text" name="identificador" value="" size="35">
			  <p>
			  <?php echo $dict_archivesaddress; ?><br>
			  <input type="text" name="logradouro" value="" size="35">
			  <p>
			  <?php echo $dict_archivescity; ?><br>
			  <input type="text" name="cidade" value="" size="35">
			  <p>
			  <?php echo $dict_archivesdistrict; ?><br>
			  <input type="text" name="estado" value="" size="35">
			  <p>
			  <?php echo $dict_archivescountry; ?>*<br>
			  <select name="pais">
					<option value="AF">Afghanistan</option>
					<option value="AX">Åland Islands</option>
					<option value="AL">Albania</option>
					<option value="DZ">Algeria</option>
					<option value="AS">American Samoa</option>
					<option value="AD">Andorra</option>
					<option value="AO">Angola</option>
					<option value="AI">Anguilla</option>
					<option value="AQ">Antarctica</option>
					<option value="AG">Antigua and Barbuda</option>
					<option value="AR">Argentina</option>
					<option value="AM">Armenia</option>
					<option value="AW">Aruba</option>
					<option value="AU">Australia</option>
					<option value="AT">Austria</option>
					<option value="AZ">Azerbaijan</option>
					<option value="BS">Bahamas</option>
					<option value="BH">Bahrain</option>
					<option value="BD">Bangladesh</option>
					<option value="BB">Barbados</option>
					<option value="BY">Belarus</option>
					<option value="BE">Belgium</option>
					<option value="BZ">Belize</option>
					<option value="BJ">Benin</option>
					<option value="BM">Bermuda</option>
					<option value="BT">Bhutan</option>
					<option value="BO">Bolivia, Plurinational State of</option>
					<option value="BQ">Bonaire, Sint Eustatius and Saba</option>
					<option value="BA">Bosnia and Herzegovina</option>
					<option value="BW">Botswana</option>
					<option value="BV">Bouvet Island</option>
					<option value="BR">Brazil</option>
					<option value="IO">British Indian Ocean Territory</option>
					<option value="BN">Brunei Darussalam</option>
					<option value="BG">Bulgaria</option>
					<option value="BF">Burkina Faso</option>
					<option value="BI">Burundi</option>
					<option value="KH">Cambodia</option>
					<option value="CM">Cameroon</option>
					<option value="CA">Canada</option>
					<option value="CV">Cape Verde</option>
					<option value="KY">Cayman Islands</option>
					<option value="CF">Central African Republic</option>
					<option value="TD">Chad</option>
					<option value="CL">Chile</option>
					<option value="CN">China</option>
					<option value="CX">Christmas Island</option>
					<option value="CC">Cocos (Keeling) Islands</option>
					<option value="CO">Colombia</option>
					<option value="KM">Comoros</option>
					<option value="CG">Congo</option>
					<option value="CD">Congo, the Democratic Republic of the</option>
					<option value="CK">Cook Islands</option>
					<option value="CR">Costa Rica</option>
					<option value="CI">Côte d'Ivoire</option>
					<option value="HR">Croatia</option>
					<option value="CU">Cuba</option>
					<option value="CW">Curaçao</option>
					<option value="CY">Cyprus</option>
					<option value="CZ">Czech Republic</option>
					<option value="DK">Denmark</option>
					<option value="DJ">Djibouti</option>
					<option value="DM">Dominica</option>
					<option value="DO">Dominican Republic</option>
					<option value="EC">Ecuador</option>
					<option value="EG">Egypt</option>
					<option value="SV">El Salvador</option>
					<option value="GQ">Equatorial Guinea</option>
					<option value="ER">Eritrea</option>
					<option value="EE">Estonia</option>
					<option value="ET">Ethiopia</option>
					<option value="FK">Falkland Islands (Malvinas)</option>
					<option value="FO">Faroe Islands</option>
					<option value="FJ">Fiji</option>
					<option value="FI">Finland</option>
					<option value="FR">France</option>
					<option value="GF">French Guiana</option>
					<option value="PF">French Polynesia</option>
					<option value="TF">French Southern Territories</option>
					<option value="GA">Gabon</option>
					<option value="GM">Gambia</option>
					<option value="GE">Georgia</option>
					<option value="DE">Germany</option>
					<option value="GH">Ghana</option>
					<option value="GI">Gibraltar</option>
					<option value="GR">Greece</option>
					<option value="GL">Greenland</option>
					<option value="GD">Grenada</option>
					<option value="GP">Guadeloupe</option>
					<option value="GU">Guam</option>
					<option value="GT">Guatemala</option>
					<option value="GG">Guernsey</option>
					<option value="GN">Guinea</option>
					<option value="GW">Guinea-Bissau</option>
					<option value="GY">Guyana</option>
					<option value="HT">Haiti</option>
					<option value="HM">Heard Island and McDonald Islands</option>
					<option value="VA">Holy See (Vatican City State)</option>
					<option value="HN">Honduras</option>
					<option value="HK">Hong Kong</option>
					<option value="HU">Hungary</option>
					<option value="IS">Iceland</option>
					<option value="IN">India</option>
					<option value="ID">Indonesia</option>
					<option value="IR">Iran, Islamic Republic of</option>
					<option value="IQ">Iraq</option>
					<option value="IE">Ireland</option>
					<option value="IM">Isle of Man</option>
					<option value="IL">Israel</option>
					<option value="IT">Italy</option>
					<option value="JM">Jamaica</option>
					<option value="JP">Japan</option>
					<option value="JE">Jersey</option>
					<option value="JO">Jordan</option>
					<option value="KZ">Kazakhstan</option>
					<option value="KE">Kenya</option>
					<option value="KI">Kiribati</option>
					<option value="KP">Korea, Democratic People's Republic of</option>
					<option value="KR">Korea, Republic of</option>
					<option value="KW">Kuwait</option>
					<option value="KG">Kyrgyzstan</option>
					<option value="LA">Lao People's Democratic Republic</option>
					<option value="LV">Latvia</option>
					<option value="LB">Lebanon</option>
					<option value="LS">Lesotho</option>
					<option value="LR">Liberia</option>
					<option value="LY">Libya</option>
					<option value="LI">Liechtenstein</option>
					<option value="LT">Lithuania</option>
					<option value="LU">Luxembourg</option>
					<option value="MO">Macao</option>
					<option value="MK">Macedonia, the former Yugoslav Republic of</option>
					<option value="MG">Madagascar</option>
					<option value="MW">Malawi</option>
					<option value="MY">Malaysia</option>
					<option value="MV">Maldives</option>
					<option value="ML">Mali</option>
					<option value="MT">Malta</option>
					<option value="MH">Marshall Islands</option>
					<option value="MQ">Martinique</option>
					<option value="MR">Mauritania</option>
					<option value="MU">Mauritius</option>
					<option value="YT">Mayotte</option>
					<option value="MX">Mexico</option>
					<option value="FM">Micronesia, Federated States of</option>
					<option value="MD">Moldova, Republic of</option>
					<option value="MC">Monaco</option>
					<option value="MN">Mongolia</option>
					<option value="ME">Montenegro</option>
					<option value="MS">Montserrat</option>
					<option value="MA">Morocco</option>
					<option value="MZ">Mozambique</option>
					<option value="MM">Myanmar</option>
					<option value="NA">Namibia</option>
					<option value="NR">Nauru</option>
					<option value="NP">Nepal</option>
					<option value="NL">Netherlands</option>
					<option value="NC">New Caledonia</option>
					<option value="NZ">New Zealand</option>
					<option value="NI">Nicaragua</option>
					<option value="NE">Niger</option>
					<option value="NG">Nigeria</option>
					<option value="NU">Niue</option>
					<option value="NF">Norfolk Island</option>
					<option value="MP">Northern Mariana Islands</option>
					<option value="NO">Norway</option>
					<option value="OM">Oman</option>
					<option value="PK">Pakistan</option>
					<option value="PW">Palau</option>
					<option value="PS">Palestinian Territory, Occupied</option>
					<option value="PA">Panama</option>
					<option value="PG">Papua New Guinea</option>
					<option value="PY">Paraguay</option>
					<option value="PE">Peru</option>
					<option value="PH">Philippines</option>
					<option value="PN">Pitcairn</option>
					<option value="PL">Poland</option>
					<option value="PT">Portugal</option>
					<option value="PR">Puerto Rico</option>
					<option value="QA">Qatar</option>
					<option value="RE">Réunion</option>
					<option value="RO">Romania</option>
					<option value="RU">Russian Federation</option>
					<option value="RW">Rwanda</option>
					<option value="BL">Saint Barthélemy</option>
					<option value="SH">Saint Helena, Ascension and Tristan da Cunha</option>
					<option value="KN">Saint Kitts and Nevis</option>
					<option value="LC">Saint Lucia</option>
					<option value="MF">Saint Martin (French part)</option>
					<option value="PM">Saint Pierre and Miquelon</option>
					<option value="VC">Saint Vincent and the Grenadines</option>
					<option value="WS">Samoa</option>
					<option value="SM">San Marino</option>
					<option value="ST">Sao Tome and Principe</option>
					<option value="SA">Saudi Arabia</option>
					<option value="SN">Senegal</option>
					<option value="RS">Serbia</option>
					<option value="SC">Seychelles</option>
					<option value="SL">Sierra Leone</option>
					<option value="SG">Singapore</option>
					<option value="SX">Sint Maarten (Dutch part)</option>
					<option value="SK">Slovakia</option>
					<option value="SI">Slovenia</option>
					<option value="SB">Solomon Islands</option>
					<option value="SO">Somalia</option>
					<option value="ZA">South Africa</option>
					<option value="GS">South Georgia and the South Sandwich Islands</option>
					<option value="SS">South Sudan</option>
					<option value="ES">Spain</option>
					<option value="LK">Sri Lanka</option>
					<option value="SD">Sudan</option>
					<option value="SR">Suriname</option>
					<option value="SJ">Svalbard and Jan Mayen</option>
					<option value="SZ">Swaziland</option>
					<option value="SE">Sweden</option>
					<option value="CH">Switzerland</option>
					<option value="SY">Syrian Arab Republic</option>
					<option value="TW">Taiwan, Province of China</option>
					<option value="TJ">Tajikistan</option>
					<option value="TZ">Tanzania, United Republic of</option>
					<option value="TH">Thailand</option>
					<option value="TL">Timor-Leste</option>
					<option value="TG">Togo</option>
					<option value="TK">Tokelau</option>
					<option value="TO">Tonga</option>
					<option value="TT">Trinidad and Tobago</option>
					<option value="TN">Tunisia</option>
					<option value="TR">Turkey</option>
					<option value="TM">Turkmenistan</option>
					<option value="TC">Turks and Caicos Islands</option>
					<option value="TV">Tuvalu</option>
					<option value="UG">Uganda</option>
					<option value="UA">Ukraine</option>
					<option value="AE">United Arab Emirates</option>
					<option value="GB">United Kingdom</option>
					<option value="US">United States</option>
					<option value="UM">United States Minor Outlying Islands</option>
					<option value="UY">Uruguay</option>
					<option value="UZ">Uzbekistan</option>
					<option value="VU">Vanuatu</option>
					<option value="VE">Venezuela, Bolivarian Republic of</option>
					<option value="VN">Viet Nam</option>
					<option value="VG">Virgin Islands, British</option>
					<option value="VI">Virgin Islands, U.S.</option>
					<option value="WF">Wallis and Futuna</option>
					<option value="EH">Western Sahara</option>
					<option value="YE">Yemen</option>
					<option value="ZM">Zambia</option>
					<option value="ZW">Zimbabwe</option>
				</select>
			  <p>
			  <?php echo $dict_archivesurl; ?><br>
			  <input type="url" name="url" value="" size="35">
			  <p>
			  <?php echo $dict_archivesemail; ?><br>
			  <input type="email" name="email" value="" size="35">
			  <p>
			  <?php echo $dict_archiveslatitude; ?>*<br><small><?php echo $this->raw($dict_decimaldegreesplease); ?>. <?php echo $this->raw($dict_howfindcoordinates); ?></small><br>
			  <input type="text" name="latitude" value="" required size="35">
			  <p>
			  <?php echo $dict_archiveslongitude; ?>*<br><small><?php echo $this->raw($dict_decimaldegreesplease); ?>. <?php echo $this->raw($dict_howfindcoordinates); ?></small><br>
			  <input type="text" name="longitude" value="" required size="35">
			  <br>
			  <br>
			  <?php echo $dict_collaborator; ?><br><small><?php echo $dict_collaboratoryou; ?></small><br>
			  <input type="text" name="contributor" value="" size="35">
			  <p>
			  <?php echo $dict_collaboratoremail; ?><br><small><?php echo $dict_collaboratoremailobs; ?></small><br>
			  <input type="text" name="contributoremail" value="" size="35">
			  <br><br>
			  <div class="g-recaptcha" data-sitekey="6LfYUxQUAAAAADfxBIQkBcT7SocM_Z1R5kZufEJN"></div>  
			  <br><br>
			  <input type="submit" value="<?php echo $dict_sendtoinclusion; ?>">
			</form> 
			</div> 
			
		<?php endif; ?>
		
		<?php if ($page=='login'): ?>
			<form action="/list" method="POST">
			
			   Login:<br>
			  <input type="text" name="user" size="20" value="">
			  <br>
			  Senha:<br>
			  <input type="password" name="pass" size="20" value="">

			  <br>
			
			  <input type="submit" value="Entrar">
			</form> 
		<?php endif; ?>
		
		
		<?php if ($page=='add-done'): ?>

			  <br> <?php echo $this->raw($dict_adddone); ?>


		<?php endif; ?>
		
		<?php if ($page=='add-fail'): ?>

			  <br> <?php echo $this->raw($dict_addfail); ?>


		<?php endif; ?>
		
		<?php if ($page=='about'): ?>
		<div style="text-align: left;">
			<?php echo $this->raw($dict_textabout); ?>

		</div>
		
		<div style="text-align: left;">
			<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
			<input type="hidden" name="cmd" value="_s-xclick">
			<input type="hidden" name="hosted_button_id" value="NKGPPEVWZBL4L">
			<table>
			<tr><td><input type="hidden" name="on0" value="Archives World Map">Archives World Map</td></tr><tr><td><select name="os0">
				<option value="Novice Cartographer">Novice Cartographer : €3,00 EUR - mensalmente</option>
				<option value="Amateur Cartographer">Amateur Cartographer : €5,00 EUR - mensalmente</option>
				<option value="True Cartographer">True Cartographer : €10,00 EUR - mensalmente</option>
				<option value="Epic Cartographer">Epic Cartographer : €15,00 EUR - mensalmente</option>
			</select> </td></tr>
			</table>
			<input type="hidden" name="currency_code" value="EUR">
			<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_subscribe_SM.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
			<img alt="" border="0" src="https://www.paypalobjects.com/pt_BR/i/scr/pixel.gif" width="1" height="1">
			</form>
		</div>
	
		
		<?php endif; ?>

		<?php if ($page=='stats'): ?>

			<div style="text-align: left;">
			<h2><?php echo $dict_statsof; ?></h2>
				<ul> 
					<li><?php echo $dict_institutionsdb; ?>

						<ul>
							<li><?php echo $qtdinstituicoes; ?></li>
						</ul>
					</li>
					<li><?php echo $dict_top10countries; ?>

						<ul>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['0']['pais']; ?>.PNG" title="<?php echo $paisesverificados['0']['pais']; ?>"> - <?php echo $paisesverificados['0']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['1']['pais']; ?>.PNG" title="<?php echo $paisesverificados['1']['pais']; ?>"> - <?php echo $paisesverificados['1']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['2']['pais']; ?>.PNG" title="<?php echo $paisesverificados['2']['pais']; ?>"> - <?php echo $paisesverificados['2']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['3']['pais']; ?>.PNG" title="<?php echo $paisesverificados['3']['pais']; ?>"> - <?php echo $paisesverificados['3']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['4']['pais']; ?>.PNG" title="<?php echo $paisesverificados['4']['pais']; ?>"> - <?php echo $paisesverificados['4']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['5']['pais']; ?>.PNG" title="<?php echo $paisesverificados['5']['pais']; ?>"> - <?php echo $paisesverificados['5']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['6']['pais']; ?>.PNG" title="<?php echo $paisesverificados['6']['pais']; ?>"> - <?php echo $paisesverificados['6']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['7']['pais']; ?>.PNG" title="<?php echo $paisesverificados['7']['pais']; ?>"> - <?php echo $paisesverificados['7']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['8']['pais']; ?>.PNG" title="<?php echo $paisesverificados['8']['pais']; ?>"> - <?php echo $paisesverificados['8']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
							<li><img src="https://map.arquivista.net/etc/flags/<?php echo $paisesverificados['9']['pais']; ?>.PNG" title="<?php echo $paisesverificados['9']['pais']; ?>"> - <?php echo $paisesverificados['9']['visits']; ?> <?php echo $dict_institutionsdb; ?></li>
						</ul>
					</li>
				</ul>
			</div>
		<?php endif; ?>
		
		<?php if ($page=='contact'): ?>
		
			<?php echo $this->raw($dict_textcontactpage); ?>

		
		<?php endif; ?>
		
				
		
		
		<?php if ($page=='thankyou'): ?>
		
			<?php echo $this->raw($dict_textthankyoupage); ?>

		
		<?php endif; ?>
		
		
		 
		<?php if ($page=='search'): ?>
		
		<section id="busca-api">
			<form action="/search/result" method="GET">
			<table width="90%">
			  <tr>
				<th width="8"><?php echo $dict_search; ?>:</th>
			  </tr>
			  <tr>
				<th width="15">
				  <input type="text" name="q" size="30" minlength="4"> 
				</th>

			  </tr>
			 <table />
			<br>
			</form> 
		</section>
		<?php endif; ?>
		
		<?php if ($page=='search-result'): ?>
		
			<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
			<!-- Middle post -->
			<ins class="adsbygoogle"
				 style="display:block"
				 data-ad-client="ca-pub-7782822980648918"
				 data-ad-slot="4084570559"
				 data-ad-format="auto"></ins>
			<script>
			(adsbygoogle = window.adsbygoogle || []).push({});
			</script>
			<hr>
			<br>
			<h3><?php echo $dict_searchresults; ?>:</b> "<?php echo $GET['q']; ?>"</h3> 
			<table width="90%" border="1">
			  <tr>
				<th width="50"><center><?php echo $dict_institution; ?></center></th>
				<th width="10"><center><?php echo $dict_archivescountry; ?></center></th>
				<th width="5"><center></center></th>
				
			  </tr>
			<?php foreach (($lista?:[]) as $item): ?>
			  <tr>
				<td><center><?php echo $item['nome']; ?></center></td>
				<td><center><?php echo $item['pais']; ?></center></td>
				<td><center><a href="https://map.arquivista.net/info/<?php echo $item['id']; ?>">info</center></td>
			  </tr>
			<?php endforeach; ?>
			</table>
		<?php endif; ?>
		<br><p>

			<hr width="80">
			<small><?php echo $this->raw($dict_awmwascreatedby); ?></small></p>
		
	 </div><!-- /.home -->

    </div><!-- /.container -->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="https://map.arquivista.net/etc/bootstrap-3.3.7-dist/js/jquery.min.js"><\/script>')</script>
    <script src="https://map.arquivista.net/etc/bootstrap-3.3.7-dist/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="https://map.arquivista.net/etc/bootstrap-3.3.7-dist/js/ie10-viewport-bug-workaround.js"></script>
	
	<?php if ($page=='search'): ?>
		<script src="https://map.arquivista.net/etc/awesomplete/awesomplete.js" async></script>
		<script>
		var ajax = new XMLHttpRequest();
		ajax.open("GET", "https://map.arquivista.net/api", true);
		ajax.onload = function() {
			var list = JSON.parse(ajax.responseText).map(function(i) { return i.nome; });
			new Awesomplete(document.querySelector("#busca-api input"),{ list: list });
		};
		ajax.send();
		</script>
	<?php endif; ?>
	
  </body>
</html> 

