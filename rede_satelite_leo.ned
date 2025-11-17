import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.StandardHost;
import inet.node.inet.Router;
import inet.common.misc.ThruputMeteringChannel;

network Rede_Satelite_LEO {
    parameters: @display("bgb=900,400");
    submodules: configurator: Ipv4NetworkConfigurator { @display("p=100,50");
}

orgA: StandardHost {
    @display("p=100,200;i=device/laptop");
}

orgB: StandardHost {
    @display("p=800,200;i=device/laptop");
}

routerA: Router {
    @display("p=250,200;i=abstract/router");
}

routerB: Router {
    @display("p=650,200;i=abstract/router");
}

satelite: Router {
    @display("p=450,100;i=space/satellite");
}

connections allowunconnected: // Rede local de cada organização
    orgA.ethg++ <--> ethernetline <--> routerA.ethg++;
    orgB.ethg++ <--> ethernetline <--> routerB.ethg++; // Enlace via satélite     (uplink + downlink)
    routerA.pppg++ <--> uplink <--> satelite.pppg++;
    satelite.pppg++ <--> downlink <--> routerB.pppg++;
}

channel ethernetline extends ThruputMeteringChannel {
    delay = 1ms;
    datarate = 100Mbps;
}

channel uplink extends ThruputMeteringChannel {
    delay = truncnormal(30ms, 2ms); // média 30ms, desvio 2ms
    datarate = 20Mbps;
    per = 0.0001;
}

channel downlink extends ThruputMeteringChannel {
    delay = truncnormal(25ms, 1.5ms); // média 25ms, desvio 1.5ms
    datarate = 100Mbps;
    per = 0.00005;
}